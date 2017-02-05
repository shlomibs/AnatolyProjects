using System;
using System.Collections.Generic;
using System.Linq;
using System.Data.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Data.OleDb;
using System.IO;

namespace Manager
{
    class DataBase
    {
        private OleDbConnection conn; // db connection handler
        public DataBase(string dbFile)
        {
            if (!File.Exists(dbFile))
                File.Create(dbFile);
            this.conn = new OleDbConnection(@"provider = Microsoft.jet.oledb.4.0; data source = " + dbFile);
            this.conn.Open();
        }

        ~DataBase()
        {
            this.conn.Close();
        }

        public object ExecQuery(string query)
        {
            OleDbCommand cmd = new OleDbCommand(query, this.conn);
            OleDbDataReader dbR = cmd.ExecuteReader();
            dbR.
        }
    }
}
