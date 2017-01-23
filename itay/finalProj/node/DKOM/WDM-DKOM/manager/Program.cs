using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Manager
{
    class Program
    {
        static void Main(string[] args)
        {
            // act according to args
            ProcessManager pM = new ProcessManager();
            pM.Run();
        }
    }
}
