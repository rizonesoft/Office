using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;
using DevExpress.Skins;
using Datum.Verbum.UnhandledExceptions;
using System.IO;
using System.Reflection;

namespace Datum.Verbum
{
    static class Program
    {

        static Mutex applicationMutex = null;

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        static extern bool SetForegroundWindow(IntPtr hWnd);
        
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main(string[] args)
        {

            Application.ThreadException += new System.Threading.ThreadExceptionEventHandler(Application_ThreadException);
            AppDomain.CurrentDomain.UnhandledException += new UnhandledExceptionEventHandler(CurrentDomain_UnhandledException);


            // get first parameter as a file name
            string fileName = string.Empty;
            if (args.Length > 0)
            {
                fileName = args[0];
            }
            
            try
            {
                bool createdNew = true;
                using (applicationMutex = new Mutex(true, "VERMEX-6F2B64B6-ECFB-403B-BD3A-E6BF5C9149D3", out createdNew))
                {
                    if (createdNew)
                    {
                        LoadSkins("DevExpress.BonusSkins.v11.2.dll");
                        SkinManager.EnableFormSkins();

                        Application.EnableVisualStyles();
                        Application.SetCompatibleTextRenderingDefault(false);
                        SkinManager.EnableFormSkins();

                        Application.Run(new MainForm(fileName));
                    }
                    else
                    {
                        Process current = Process.GetCurrentProcess();
                        foreach (Process process in Process.GetProcessesByName(current.ProcessName))
                        {
                            if (process.Id != current.Id)
                            {
                                SetForegroundWindow(process.MainWindowHandle);
                                break;
                            }
                        }
                    }
                }
            }
            catch (Exception mExc)
            { Application_ThreadException(MainForm.ActiveForm, new ThreadExceptionEventArgs(mExc)); }
            
        }

        private static void LoadSkins(string skinFileName)
        {
            if (File.Exists(skinFileName))
            {
                Assembly verbumAssembly = Assembly.LoadFile(Path.GetFullPath(skinFileName));
                DevExpress.Skins.SkinManager.Default.RegisterAssembly(verbumAssembly);
            }
        }

        private static void Application_ThreadException(object sender, ThreadExceptionEventArgs e)
        {
            Cataloguing.WriteBugToFile(String.Format("UNHANDLED EXCEPTION ~ THREAD ~ {0}", e.Exception.Message.ToString()));
            new exceptionForm(e.Exception).ShowDialog();
        }

        private static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            Cataloguing.WriteBugToFile("UNHANDLED EXCEPTION ~ Current Domain");
            new exceptionForm(e.ExceptionObject as Exception).ShowDialog();
        }

    }
}
