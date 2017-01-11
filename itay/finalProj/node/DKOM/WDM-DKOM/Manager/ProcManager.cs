using System;
using System.Diagnostics;
using System.IO;

namespace Manager
{
    class ProcManager
    {
        #region constants
        private const int COMMUNICATION_PROCESS_IND = 0;
        private const int DECISIONS_PROCESS_IND = 1;
        private const int MAIN_PROCESSES_NUM = 2; // TEMP for now
        #endregion

        #region variables
        private ProcessHider procHider;
        private Process[] MainProcesses;
        private bool shutdown;
        #endregion

        public ProcManager()
        {
            procHider = new ProcessHider();
            MainProcesses = new Process[3];
            shutdown = false;
        }

        public void setShutdown()
        {
            this.shutdown = true;
        }

        public void Run()
        {
            //this.MainProcesses[COMMUNICATION_PROCESS_IND] = procHider.StartHiddenProcess();
            //this.MainProcesses[DECISIONS_PROCESS_IND] = procHider.StartHiddenProcess();
            while (!this.shutdown) // passing data and commands between parts and opening new threads for tasks
            {

            }
        }
    }
}

