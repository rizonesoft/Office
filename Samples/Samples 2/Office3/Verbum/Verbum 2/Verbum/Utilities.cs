using System.Collections;
using System.Windows.Forms;
using System;
using System.Diagnostics;


namespace Rizonesoft.Verbum
{
    class Utilities
    {
        public static Hashtable availableDictionaries = new Hashtable();

        //public static bool settFormSkins = false;
        public static string settSpellingLanguage = "en-US";
        public static bool settEnableAutoSpellCheck = true;
        public static bool initRun = true;

        public static FormWindowState settFormWinState = FormWindowState.Normal;

        public static int countDocX = 0;
        public static int countDocY = 0;
        
        public static void SetWorkingSet(int lnMaxSize, int lnMinSize)
        {
            Process loProcess = Process.GetCurrentProcess();

            loProcess.MaxWorkingSet = (IntPtr)lnMaxSize;
            loProcess.MinWorkingSet = (IntPtr)lnMinSize;
        }
    }

}
