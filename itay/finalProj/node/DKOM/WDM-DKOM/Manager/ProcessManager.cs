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
        #endregion

        #region variables
        private ProcessHider procHider;
        private Process[] mainProcesses;
        private List<Process> secondaryProcesses;
        private bool shutdown;
        #endregion

        public ProcessManager()
        {
            procHider = new ProcessHider();
            mainProcesses = new Process[MAIN_PROCESSES_NUM];
            secondaryProcesses = new List<Process>();
            shutdown = false;
            //procHider.HideProc(Process.GetCurrentProcess());
        }

        public void setShutdown()
        {
            this.shutdown = true;
        }

        /// <summary>
        /// manager main loop
        /// </summary>
        public void Run()
        {
            // python -u = python unbuffered -> disable the need for sys.stdout.flush() after every print
            if (!this.StartProcess("python", @"-u G:\programming\AnatolyProjects\itay\print.py", this.OutputDataReceived, out this.mainProcesses[COMMUNICATION_PROCESS_IND]) ||
                !this.StartProcess(@"G:\programming\AnatolyProjects\itay\print.bat", "", this.OutputDataReceived, out this.mainProcesses[DECISIONS_PROCESS_IND]))
                Environment.Exit(-1); // could not start main processes

            while (!this.shutdown) // passing data and commands between parts and opening new threads for tasks
            {
                if (Console.ReadKey().Key == ConsoleKey.Escape)
                {
                    Console.WriteLine("exiting: ");
                    foreach (var proc in this.mainProcesses)
                    {
                        if (!proc.HasExited)
                        {
                            Console.Write("exiting {0} ({1})...", proc.ProcessName, proc.Id);
                            proc.Kill();
                            Console.WriteLine("\t\t\t\t exited");
                        }
                    }
                    //this.mainProcesses[COMMUNICATION_PROCESS_IND].Kill();
                    //this.mainProcesses[DECISIONS_PROCESS_IND].Kill();
                    break;
                }
                else
                {
                    //Console.WriteLine(this.mainProcesses[COMMUNICATION_PROCESS_IND].StandardOutput.Read());
                }
            }
        }

        void OutputDataReceived(object sender, DataReceivedEventArgs e)
        {
            if(!String.IsNullOrEmpty(e.Data))
                Console.WriteLine(e.Data);
        }

        private void KillSecondaryProcess(Process p)
        {
            this.secondaryProcesses.Remove(p);
            p.Kill();
        }

        /// <summary>
        /// starts a process
        /// </summary>
        /// <param name="path"></param>
        /// <param name="args"></param>
        /// <param name="outProc"></param>
        /// <returns> true if succeeded</returns>
        private bool StartProcess(string path, string args, out Process outProc)
        {
            if (!System.Environment.Is64BitOperatingSystem) // temp
                outProc = this.procHider.StartHiddenProcess(path, args);
            else
                outProc = this.procHider.StartVisibleProcess(path, args);
            if (outProc == null)
                return false;
            return true;
        }

        /// <summary>
        /// starts a process
        /// </summary>
        /// <param name="path"></param>
        /// <param name="args"></param>
        /// <param name="outProc"></param>
        /// <returns> true if succeeded</returns>
        private bool StartProcess(string path, string args, DataReceivedEventHandler outputHandler, out Process outProc)
        {
            if (!System.Environment.Is64BitOperatingSystem) // temp
                outProc = this.procHider.StartHiddenProcess(path, args, outputHandler);
            else
                outProc = this.procHider.StartVisibleProcess(path, args, outputHandler);
            if (outProc == null)
                return false;
            return true;
        }
    }
}

