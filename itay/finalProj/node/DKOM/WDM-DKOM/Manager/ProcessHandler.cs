#define DEBUG
#define CHECK_OS // for testing
// if DKOM will work on 64bit OS then undefine it

using System;
using System.Diagnostics;
using System.IO;

namespace Manager
{
    class ProcessHandler
    {
        #region fields
        private ProcessHider procHider;
        private Process processObj;
        private StreamWriter stdin;
        private DataReceivedEventHandler outEvntHandler;
        private DataReceivedEventHandler errEvntHandler;
        private EventHandler exitEvntHandler;
#if DEBUG
        private string name;
        private static StreamWriter Log = null;
#endif
        #endregion

        const bool DKOM = false;

        public Process process { get { return processObj; } } // returns a reference to the process
        public bool IsRunning { get { return this.processObj != null && !this.processObj.HasExited; } }

        public ProcessHandler(ProcessHider procHider)
        {
            this.procHider = procHider;
            this.outEvntHandler += (s, e) => { }; // to prevent null reference exception
            this.errEvntHandler += (s, e) => { };
            this.exitEvntHandler += (s, e) =>
            {
#if DEBUG
                Console.WriteLine(this.name + " || exited, data: " + e.ToString());
                Log.WriteLine(this.name + " || exited, data: " + e.ToString());
#endif
            };
#if DEBUG
            if (Log == null)
            {
                Log = new StreamWriter("log.log");
                Log.AutoFlush = true;
            }
#endif
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
            if (!System.Environment.Is64BitOperatingSystem && DKOM) // temp
                processObj = this.procHider.StartHiddenProcess(path, args, exitEvntHandler, outEvntHandler, errEvntHandler, out stdin);
            else
            {
                processObj = this.procHider.StartVisibleProcess(path, args);
                this.stdin = processObj.StandardInput;
                processObj.OutputDataReceived += (s, e) => { this.outEvntHandler(s, e); };
                processObj.ErrorDataReceived += (s, e) => { this.errEvntHandler(s, e); };
                processObj.Exited += (s, e) => { this.exitEvntHandler(s, e); };
            }
#if DEBUG
            this.name = path + " " + args;
            Log.WriteLine(this.name + " started");
            Console.WriteLine(this.name + " started");
            DataReceivedEventHandler Logger = (s, e) =>
            {
                lock (Log)
                {
                    try
                    {
                        Console.WriteLine(process.ProcessName + ", " + this.name + " >> manager: " + e.Data);
                        Log.WriteLine(process.ProcessName + ", " + this.name + " >> manager: " + e.Data);
                    }
                    catch (Exception e1)
                    {
                        Console.WriteLine(this.name + " >> thrown exception, probably exited, exception: " + e1.ToString());
                        Log.WriteLine(this.name + " >> thrown exception, probably exited, exception: " + e1.ToString());
                    }
                    Log.Flush();
                }
            };
            this.outEvntHandler += Logger;
            this.errEvntHandler += Logger;
#endif
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
            if (!System.Environment.Is64BitOperatingSystem && DKOM) // temp
#endif
                processObj = this.procHider.StartHiddenProcess(path, args, exitEvntHandler, outEvntHandler, errEvntHandler, out stdin);
#if (CHECK_OS)
            else
            {
                processObj = this.procHider.StartVisibleProcess(path, args, outputHandler);
                this.stdin = processObj.StandardInput;
                processObj.OutputDataReceived += (s, e) => { this.outEvntHandler(s, e); };
                processObj.ErrorDataReceived += (s, e) => { this.errEvntHandler(s, e); };
                processObj.Exited += (s, e) => { this.exitEvntHandler(s, e); };
            }
#endif

#if DEBUG
            this.name = path + " " + args;
            Log.WriteLine(this.name + " started");
            Console.WriteLine(this.name + " started");
            DataReceivedEventHandler Logger = (s, e) =>
            {
                lock (Log)
                {
                    try
                    {
                        Console.WriteLine(process.ProcessName + ", " + this.name + " >> manager: " + e.Data);
                        Log.WriteLine(process.ProcessName + ", " + this.name + " >> manager: " + e.Data);
                    }
                    catch (Exception e1)
                    {
                        Console.WriteLine(this.name + " >> thrown exception, probably exited, exception: " + e1.ToString());
                        Log.WriteLine(this.name + " >> thrown exception, probably exited, exception: " + e1.ToString());
                    }
                    Log.Flush();
                }
            };
            this.outEvntHandler += Logger;
            this.errEvntHandler += Logger;
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
        public bool StartProcess(string cmd, ProcessHandler outputProcess)
        {
            string[] splt = cmd.Split(','); // {taskId, filename, args}
            if (splt.Length != 3)
                throw new Exception("wrong format command: " + cmd);
            //return false;

            // pass output data via stdin
            DataReceivedEventHandler outputHandler = (s, e) =>
            {
                if (!String.IsNullOrEmpty(e.Data))
                    lock (outputProcess)
                        outputProcess.SendData(ProcessManager.PROCESS_DATA_CODE + splt[0] /* task id */ + "," + e.Data);
            };


            // TODO: option - output to file
            //DataReceivedEventHandler outputHandler = (s, e) => // write the output to file
            //{
            //    StreamWriter sw = new StreamWriter(splt[2]); // create new file or clear existing one
            //    sw.Write(e.Data);
            //    sw.Close();
            //};
            try
            {
                return this.StartProcess(splt[1], splt[2], outputHandler);
            }
            catch(Exception e)
            {
                string errData = String.Join("\n" + ProcessManager.PROCESS_DATA_CODE + splt[0]/* task id */ + ", ", e.ToString().Split('\n'));
                lock (outputProcess)
                    outputProcess.SendData(ProcessManager.PROCESS_DATA_CODE + splt[0] /* task id */ + ",error: " + errData);
                return false;
            }
        }

        /// <summary>
        ///  add output handler to the process
        /// </summary>
        /// <param name="outputHandler"> the function to handle the process </param>
        /// <returns> true if the operation succeeded </returns>
        public bool AddOutputHandler(DataReceivedEventHandler outputHandler)
        {
            if (this.processObj == null || this.processObj.HasExited)
                return false;
            outEvntHandler += outputHandler;
            errEvntHandler += outputHandler;
            //this.processObj.OutputDataReceived += outputHandler;
            //this.processObj.ErrorDataReceived += outputHandler;
            return true;
        }

        /// <summary>
        /// removes output handler from the process
        /// </summary>
        /// <param name="outputHandler"> the handler to remove </param>
        /// <returns> true if the operation succeeded </returns>
        public bool RemoveOutputHandler(DataReceivedEventHandler outputHandler)
        {
            if (this.processObj == null || this.processObj.HasExited)
                return false;
            try
            {
                this.outEvntHandler -= outputHandler;
                this.errEvntHandler -= outputHandler;
            }
            catch (Exception e) // if the event handler not exist in the list
            {
#if DEBUG
                Console.WriteLine("Exception occured in process: " + process.ProcessName + "\nat ProcessHandler.RemoveOutputHandler: " + e);
#endif
                return false;
            }
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
            this.exitEvntHandler += exitHandler;
            return true;
        }

        /// <summary>
        /// send data to the process via stdin
        /// </summary>
        /// <param name="data"> the data to deliver </param>
        public void SendData(string data)
        {
#if DEBUG
            lock (Log)
            {
                Console.WriteLine("manager >> " + this.name + ": " + data);
                Log.WriteLine("manager >> " + this.name + ": " + data);
                Log.Flush();
            }
#endif
            lock (this.process.StandardInput)
                this.stdin.WriteLine(data);
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
