using System;
using System.Diagnostics;
using System.Linq;

namespace Manager
{
    class Program
    {
        private static ProcessManager pM;
        private const string PROG_NAME = "Manager.exe";
        static void Main(string[] args)
        {
            // act according to args
            AppDomain.CurrentDomain.ProcessExit += CurrentDomain_ProcessExit;
            pM = new ProcessManager();
            pM.Run();
        }

        private static void CurrentDomain_ProcessExit(object sender, EventArgs e)
        {
            pM.Shutdown();
            Process.Start(PROG_NAME); // now restart the program
        }
    }
}
