using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
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
        private const string databaseFile = @"db\db.db";
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
            //procHider.HideProc(Process.GetCurrentProcess());
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
                !this.mainProcesses[DECISIONS_PROCESS_IND].StartProcess("python" , @"-u Decision\decider.py", this.OnDecisionRecieved) ||
                !this.mainProcesses[DATABASE_PROCESS_IND].StartProcess("python", @"-u Database\database.py " + ProcessManager.databaseFile))
                Environment.Exit(-1); // could not start main processes

            DatabaseThread(); // starts the thread if it is in the main thread

            //if (!this.mainProcesses[COMMUNICATION_PROCESS_IND].StartProcess("python", @"-u G:\programming\AnatolyProjects\itay\print.py", this.OutputDataReceived) ||
            //    !this.mainProcesses[DECISIONS_PROCESS_IND].StartProcess(@"G:\programming\AnatolyProjects\itay\print.bat", "", this.OutputDataReceived))
            //    Environment.Exit(-1); // could not start main processes

            while (!this.shutdown) // passing data and commands between parts and opening new threads for tasks
            {
                if (Console.ReadKey().Key == ConsoleKey.Escape)
                {
                    break;
                }
                else
                {
                   // for checks
                }
            }
        }

        private void DatabaseThread()
        {
            if (Thread.CurrentThread.ManagedThreadId == mainThreadId) // not started as a seperate thread
            {
                //throw new Exception("db queries must be running in a seperate thread");
                Thread dbThread = new Thread(DatabaseThread);
                dbThread.Start();
            }
            while (!this.shutdown)
            {
                // lock is not needed because Count returns a variable and not counts the queries
                while (this.Queries.Count > 0) // while not empty
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
            switch (e.Data[0])
            {
                case SEND_CMD:
                    lock (this.mainProcesses[COMMUNICATION_PROCESS_IND])
                        this.mainProcesses[COMMUNICATION_PROCESS_IND].SendData(e.Data.Substring(1)); // pass data without command
                        // NOTICE: the data is a filename with the data
                    break;
                case START_PROCESS_CMD: // the data should be: <command type char><proccess identification string>,
                    ProcessHandler newProc = new ProcessHandler(this.procHider);
                    lock (this.secondaryProcesses)
                        this.secondaryProcesses.Add(newProc);
                    newProc.StartProcess(e.Data.Substring(1), this.mainProcesses[DECISIONS_PROCESS_IND]); // remove command character
                    EventHandler exitHandler = (s, e2) =>
                    {
                        lock (this.mainProcesses[DECISIONS_PROCESS_IND])
                            this.mainProcesses[DECISIONS_PROCESS_IND].SendData(ProcessManager.PROCESS_ENDED_CODE + e.Data.Split(',')[0].Substring(1));
                        // equals to START_PROCESS_CMD + e.Data.Split(',')[0].Substring(1)
                        lock (this.secondaryProcesses)
                            this.secondaryProcesses.Remove(newProc);
                    };
                    newProc.AddExitHandler(exitHandler);
                    break;
                case QUERY_CMD:
                    lock(Queries)
                    {
                        Queries.Enqueue(e.Data.Substring(1)); // the queued commands will be executed in another thread
                    }
                    break;
                case DISPLAY_CODE:
                    if (!this.isAdminConnected)
                    {
                        if (e.Data[1] != '\'' && e.Data[1] != '"') // not repr'd => try to connect from another controller
                        {
                            isAdminConnected = true;
                            this.controllerProcess = new ProcessHandler(this.procHider);
                            this.controllerProcess.StartProcess("python", @"-u controllerConnection\controllerConnection.py " + e.Data.Substring(1));
                            this.controllerProcess.AddExitHandler((s, e2) => { isAdminConnected = false; });
                            this.controllerProcess.AddOutputHandler(OnControllerRecieved);
                        }
                        //else drop the message
                    }
                    else
                    {
                        if (e.Data[1] != '\'' && e.Data[1] != '"') // not repr'd => try to connect from another controller
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
                                this.controllerProcess.SendData(e.Data.Substring(1));
                    }
                    break;
                default:
                    throw new InvalidOperationException("Unknown command");
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

