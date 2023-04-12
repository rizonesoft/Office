namespace Rizonesoft.Office.Interprocess
{
    using System.Diagnostics;
    using System.IO;
    using System.Runtime.InteropServices;

    public class CopyDataEx
    {
        private const int WM_COPYDATA = 0x004A;

        [DllImport("user32.dll")]
        private static extern int SendMessage(IntPtr hWnd, int Msg, IntPtr wParam, ref COPYDATASTRUCT lParam);

        [StructLayout(LayoutKind.Sequential)]
        private struct COPYDATASTRUCT
        {
            public IntPtr dwData;
            public int cbData;
            public IntPtr lpData;
        }

        public static void OpenFileInProcess(string processName, string filePath)
        {
            var processes = Process.GetProcessesByName(processName);
            if (processes.Length == 0)
            {
                // No running process with this name.
                // TODO: Handle error appropriately.
                return;
            }

            // Get the first process with this name.
            var process = processes[0];

            // Convert the file path to bytes.
            var bytes = System.Text.Encoding.Unicode.GetBytes(filePath);

            // Allocate memory in the process and copy the file path bytes to it.
            var mem = NativeMethods.VirtualAllocEx(process.Handle, IntPtr.Zero, bytes.Length, NativeMethods.AllocationType.Commit, NativeMethods.MemoryProtection.ReadWrite);
            NativeMethods.WriteProcessMemory(process.Handle, mem, bytes, bytes.Length, out _);

            // Send the file path to the process.
            var cds = new COPYDATASTRUCT
            {
                dwData = IntPtr.Zero,
                cbData = bytes.Length,
                lpData = mem
            };
            SendMessage(process.MainWindowHandle, WM_COPYDATA, IntPtr.Zero, ref cds);

            // Free the memory in the process.
            NativeMethods.VirtualFreeEx(process.Handle, mem, 0, NativeMethods.AllocationType.Release);
        }
    }

    internal static class NativeMethods
    {
        [DllImport("kernel32.dll", SetLastError = true)]
        internal static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, int dwSize, AllocationType flAllocationType, MemoryProtection flProtect);

        [DllImport("kernel32.dll", SetLastError = true)]
        internal static extern bool VirtualFreeEx(IntPtr hProcess, IntPtr lpAddress, int dwSize, AllocationType dwFreeType);

        [DllImport("kernel32.dll", SetLastError = true)]
        internal static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, int nSize, out int lpNumberOfBytesWritten);

        [Flags]
        internal enum AllocationType
        {
            Commit = 0x1000,
            Reserve = 0x2000,
            Decommit = 0x4000,
            Release = 0x8000,
            Reset = 0x80000,
            TopDown = 0x100000,
            WriteWatch = 0x200000,
            Physical = 0x400000,
            LargePages = 0x20000000
        }

        [Flags]
        internal enum MemoryProtection
        {
            NoAccess = 0x01,
            ReadOnly = 0x02,
            ReadWrite = 0x04,
            WriteCopy = 0x08,
            Execute = 0x10,
            ExecuteRead = 0x20,
            ExecuteReadWrite = 0x40,
            ExecuteWriteCopy = 0x80,
            Guard = 0x100,
            NoCache = 0x200,
            WriteCombine = 0x400
        }
    }
}
