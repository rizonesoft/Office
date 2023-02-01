using System;
using System.Windows.Forms;
using System.Reflection;
using System.Runtime.InteropServices;


namespace Rizone.Verbum
{
    /// <summary>
    /// Description of EnvironmentInfo.
    /// </summary>
    public class EnvironmentInfo
    {
        private EnvironmentInfo() { }

        public static string EnvironmentToString()
        {
            string r = "Software version: " + Application.ProductVersion + "\r\n";
            r += ".NET runtime version: " + Assembly.GetEntryAssembly().ImageRuntimeVersion + "\r\n";
            r += "Time: " + DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss zzz") + "\r\n";
            r += "OS: " + OSName + " Build " + OSBuild + " " + OSServicePack + "\r\n";
            return r;
        }

        public static string ExceptionToString(Exception ex)
        {
            if (ex == null)
                return "null\n";

            string report = "";
            report += "Exception: " + ex.GetType().ToString() + "\r\n";
            report += "Message: " + ex.Message + "\r\n";
            report += "Stack:\r\n" + ex.StackTrace + "\r\n";
            if (ex is ExternalException)   // e.g. COMException
                report += "ErrorCode: " + (ex as ExternalException).ErrorCode.ToString() + "\r\n";
            if (ex.InnerException != null)
            {
                report += "--- InnerException: ---\r\n";
                report += ExceptionToString(ex.InnerException);
            }
            return report;
        }

        #region OS version detection

        /// <summary>
        /// Enumeration of known operating systems
        /// </summary>
        public enum OSVersionEnum : int
        {
            /// <summary>
            /// Unknown
            /// </summary>
            Unknown = 0,
            /// <summary>
            /// Microsoft Windows 95
            /// </summary>
            Win95,
            /// <summary>
            /// Microsoft Windows 98
            /// </summary>
            Win98,
            /// <summary>
            /// Microsoft Windows ME
            /// </summary>
            WinME,
            /// <summary>
            /// Microsoft Windows NT 4.0
            /// </summary>
            WinNT4,
            /// <summary>
            /// Microsoft Windows 2000
            /// </summary>
            Win2000,
            /// <summary>
            /// Microsoft Windows XP
            /// </summary>
            WinXP,
            /// <summary>
            /// Microsoft Windows Server 2003
            /// </summary>
            Win2003,
            /// <summary>
            /// Microsoft Windows Vista
            /// </summary>
            WinVista
        }

        public static OSVersionEnum OSVersion
        {
            get
            {
                OperatingSystem os = Environment.OSVersion;
                if (os.Platform == PlatformID.Win32Windows && os.Version.Major >= 4 && os.Version.Minor == 0)
                    return OSVersionEnum.Win95;
                if (os.Platform == PlatformID.Win32Windows && os.Version.Major >= 4 && os.Version.Minor > 0 && os.Version.Minor < 90)
                    return OSVersionEnum.Win98;
                if (os.Platform == PlatformID.Win32Windows && os.Version.Major >= 4 && os.Version.Minor >= 90)
                    return OSVersionEnum.WinME;
                if (os.Platform == PlatformID.Win32NT && os.Version.Major <= 4)
                    return OSVersionEnum.WinNT4;
                if (os.Platform == PlatformID.Win32NT && os.Version.Major == 5 && os.Version.Minor == 0)
                    return OSVersionEnum.Win2000;
                if (os.Platform == PlatformID.Win32NT && os.Version.Major == 5 && os.Version.Minor == 1)
                    return OSVersionEnum.WinXP;
                if (os.Platform == PlatformID.Win32NT && os.Version.Major == 5 && os.Version.Minor == 2)
                    return OSVersionEnum.Win2003;
                if (os.Platform == PlatformID.Win32NT && os.Version.Major == 6 && os.Version.Minor == 0)
                    return OSVersionEnum.WinVista;
                return OSVersionEnum.Unknown;
            }
        }

        public static bool Is64Bit
        {
            get
            {
                return IntPtr.Size == 8;
            }
        }

        public static string OSName
        {
            get
            {
                switch (OSVersion)
                {
                    case OSVersionEnum.Win95: return "Windows 95";
                    case OSVersionEnum.Win98: return "Windows 98";
                    case OSVersionEnum.WinME: return "Windows ME";
                    case OSVersionEnum.WinNT4: return "Windows NT 4";
                    case OSVersionEnum.Win2000: return "Windows 2000";
                    case OSVersionEnum.WinXP: return "Windows XP" + (Is64Bit ? " x64" : "");
                    case OSVersionEnum.Win2003: return "Windows Server 2003" + (Is64Bit ? " x64" : "");
                    case OSVersionEnum.WinVista: return "Windows Vista" + (Is64Bit ? " x64" : "");
                }
                return "";
            }
        }

        public static string OSBuild
        {
            get
            {
                OperatingSystem os = Environment.OSVersion;
                return os.Version.Build.ToString();
            }
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct OSVERSIONINFO
        {
            public int dwOSVersionInfoSize;
            public int dwMajorVersion;
            public int dwMinorVersion;
            public int dwBuildNumber;
            public int dwPlatformId;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
            public string szCSDVersion;
        }
        [DllImport("kernel32.Dll")]
        public static extern short GetVersionEx(ref OSVERSIONINFO o);
        static public string OSServicePack
        {
            get
            {
                OSVERSIONINFO os = new OSVERSIONINFO();
                os.dwOSVersionInfoSize = Marshal.SizeOf(typeof(OSVERSIONINFO));
                GetVersionEx(ref os);
                return os.szCSDVersion;
            }
        }

        #endregion OS version detection

    }
}