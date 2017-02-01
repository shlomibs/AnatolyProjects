using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;

namespace Manager
{
    class ProcessManager
    {
        #region constants
        private const int COMMUNICATION_PROCESS_IND = 0;
        private const int DECISIONS_PROCESS_IND = 1;
        private const int MAIN_PROCESSES_NUM = 2; // TEMP for now
        private const char SEND_CMD = 's';
        private const char START_PROCESS_CMD = 'p';
        private const char PROCESS_ENDED_CODE = 'e';
        private const string MAIN_SHUTDOWN_CODE = "SHUTDOWN"; // not used yet
        public const char PROCESS_DATA_CODE = 'd';
        #endregion

        #region fields
        private ProcessHider procHider;
        private ProcessHandler[] mainProcesses;
        private List<ProcessHandler> secondaryProcesses;
        private bool shutdown;
        #endregion

        public ProcessManager()
        {
            procHider = new ProcessHider();
            mainProcesses = new ProcessHandler[MAIN_PROCESSES_NUM];
            secondaryProcesses = new List<ProcessHandler>();
            shutdown = false;
            Directory.CreateDirectory("temp"); // for output files or executables i.e. python code or batch files
            //procHider.HideProc(Process.GetCurrentProcess());
        }

        /// <summary>
        /// call to shutdown the manager
        /// </summary>
        public void Shutdown()
        {
            this.shutdown = true;
            foreach (var procH in this.secondaryProcesses) // kill all
                procH.Kill();
            foreach (var procH in this.mainProcesses)
                procH.Kill();
            this.mainProcesses = new ProcessHandler[MAIN_PROCESSES_NUM];
            this.secondaryProcesses = new List<ProcessHandler>();
        }

        /// <summary>
        /// manager main loop
        /// </summary>
        public void Run()
        {
            for (int i = 0; i < this.mainProcesses.Length; i++)
                this.mainProcesses[i] = new ProcessHandler(this.procHider);
            // python -u = python unbuffered -> disable the need for sys.stdout.flush() after every print
            if (!this.mainProcesses[COMMUNICATION_PROCESS_IND].StartProcess("python", @"-u Communication\communicator.py", this.OnCommunicationReceived) ||
                !this.mainProcesses[DECISIONS_PROCESS_IND].StartProcess(@"Decision\decider.py", "", this.OnDecisionRecieved))
                Environment.Exit(-1); // could not start main processes

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

        private void OnCommunicationReceived(object sender, DataReceivedEventArgs e)
        {
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
                    this.mainProcesses[COMMUNICATION_PROCESS_IND].SendData(e.Data.Substring(1)); // pass data without command
                    // NOTICE: the data is a filename with the data
                    break;
                case START_PROCESS_CMD: // the data should be: <command type char><proccess identification string>,
                    ProcessHandler newProc = new ProcessHandler(this.procHider);
                    newProc.StartProcess(e.Data.Substring(1)); // remove command character
                    EventHandler exitHandler = (s,e2) =>
                    {
                        this.mainProcesses[DECISIONS_PROCESS_IND].SendData(ProcessManager.PROCESS_ENDED_CODE + e.Data.Split(',')[0].Substring(1));
                        // equals to START_PROCESS_CMD + e.Data.Split(',')[0].Substring(1)
                        this.secondaryProcesses.Remove(newProc);
                    };
                    newProc.AddExitHandler(exitHandler);
                    this.secondaryProcesses.Add(newProc);
                    break;
                default:
                    throw new Exception("Unknown command");
            }
            //throw new NotImplementedException();
        }

        // test event handler:
        object testLock = new object();
        void OutputDataReceived(object sender, DataReceivedEventArgs e)
        {
            if (!String.IsNullOrEmpty(e.Data))
            {
                Console.WriteLine(e.Data);
                lock (testLock)
                {
                    StreamWriter sw = new StreamWriter("g:\\log.log", true);
                    sw.WriteLine(e.Data);//Encoding.Convert(Encoding.ASCII, Encoding.Unicode, Encoding.ASCII.GetBytes(e.Data)));
                    sw.Close();
                }
                ((Process)sender).StandardInput.WriteLine(e.Data);
                ((Process)sender).StandardInput.Flush();
                //((Process)sender).StandardInput.BaseStream.Flush();
            }
        }

        private void KillSecondaryProcess(ProcessHandler p)
        {
            this.secondaryProcesses.Remove(p);
            p.Kill();
        }


    }
}

