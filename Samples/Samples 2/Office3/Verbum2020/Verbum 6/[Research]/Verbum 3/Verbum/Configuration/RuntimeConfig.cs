using System;
using System.IO;
using System.Windows.Forms;


namespace Rizonesoft.Verbum.Configuration
{

    public abstract class RuntimeConfig
    {
        public static string userAppDataDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "Rizonesoft\\Verbum");
    }
}
