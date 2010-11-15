using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;

namespace WebLab.VM.WindowsVNC
{
    public class IniRW : IDisposable
    {
        public string filePath;

        [DllImport("kernel32")]
        private static extern long WritePrivateProfileString(string section,
          string key, string val, string filePath);

        [DllImport("kernel32")]
        private static extern int GetPrivateProfileString(string section,
          string key, string def, StringBuilder retVal,
          int size, string filePath);

        public IniRW(string filePath)
        {
            this.filePath = filePath;
        }

        public void WriteValue(string section, string key, string val)
        {
            WritePrivateProfileString(section, key, val, this.filePath);
        }

        public string ReadValue(string section, string key)
        {
            StringBuilder sb = new StringBuilder(1024);
            GetPrivateProfileString(section, key, "", sb, 1024, this.filePath);
            return sb.ToString();
        }

        public void Dispose()
        {
        }
    }
}
