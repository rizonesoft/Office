using System.Collections;
using System.Runtime.InteropServices;

namespace Rizonesoft.Office.Framework
{
    /// <summary>
    /// EnumWindows wrapper for .NET. Provides functionality to enumerate through all top-level windows.
    /// </summary>
    public partial class EnumWindows
    {
        /// <summary>
        /// Delegate for handling the enumeration of windows.
        /// </summary>
        /// <param name="hwnd">The handle of the current window in the enumeration.</param>
        /// <param name="lParam">An application-defined value given in EnumWindows.</param>
        /// <returns>Nonzero to continue enumeration, zero to stop enumeration.</returns>
        public delegate int EnumWindowsProc(IntPtr hwnd, int lParam);

        /// <summary>
        /// Contains methods for unmanaged code operations.
        /// </summary>
        public static partial class UnManagedMethods
        {
            /// <summary>
            /// Enumerates all top-level windows on the screen by passing the handle to each window, in turn, to an application-defined callback function.
            /// </summary>
            /// <param name="lpEnumFunc">A pointer to an application-defined callback function.</param>
            /// <param name="lParam">An application-defined value to be passed to the callback function.</param>
            [LibraryImport("user32")]
            public static partial void EnumWindows(EnumWindowsProc lpEnumFunc, int lParam);
        }

        /// <summary>
        /// Gets the collection of windows returned by GetWindows.
        /// </summary>
        public EnumWindowsCollection? Items { get; private set; }

        /// <summary>
        /// Retrieves all top level windows on the system.
        /// </summary>
        /// <exception cref="System.ComponentModel.Win32Exception">Thrown when there is an error retrieving the windows.</exception>
        public void GetWindows()
        {
            Items = new EnumWindowsCollection();
            UnManagedMethods.EnumWindows(WindowEnum, 0);
        }

        /// <summary>
        /// Callback function for the EnumWindows method.
        /// </summary>
        /// <param name="hWnd">Window Handle.</param>
        /// <param name="lParam">Application defined value.</param>
        /// <returns>1 to continue enumeration, 0 to stop.</returns>
        private int WindowEnum(IntPtr hWnd, int lParam)
        {
            return OnWindowEnum(hWnd) ? 1 : 0;
        }

        /// <summary>
        /// Called whenever a new window is about to be added by the Window enumeration called from GetWindows.
        /// </summary>
        /// <param name="hWnd">Window handle to add.</param>
        /// <returns>True to continue enumeration, False to stop.</returns>
        protected virtual bool OnWindowEnum(IntPtr hWnd)
        {
            Items?.Add(hWnd);
            return true;
        }

        /// <summary>
        /// Constructor of EnumWindows.
        /// </summary>
        public EnumWindows()
        {
            // nothing to do
        }
    }

    /// <summary>
    /// Represents a collection of windows returned by GetWindows.
    /// </summary>
    public class EnumWindowsCollection : ReadOnlyCollectionBase
    {
        /// <summary>
        /// Add a new window to the collection. Intended for internal use by EnumWindows only.
        /// </summary>
        /// <param name="hWnd">Window handle to add.</param>
        public void Add(IntPtr hWnd)
        {
            var item = new EnumWindowsItem(hWnd);
            InnerList.Add(item);
        }

        /// <summary>
        /// Constructor of EnumWindowsCollection.
        /// </summary>
        public EnumWindowsCollection()
        {
            // nothing to do
        }
    }

    /// <summary>
    /// Represents the details about a window returned by the enumeration.
    /// </summary>
    public class EnumWindowsItem
    {
        /// <summary>
        /// Gets the window's handle.
        /// </summary>
        public IntPtr Handle { get; }

        /// <summary>
        /// Constructs a new instance of this class for the specified window handle.
        /// </summary>
        /// <param name="hWnd">The window handle.</param>
        public EnumWindowsItem(IntPtr hWnd)
        {
            this.Handle = hWnd;
        }
    }
}
