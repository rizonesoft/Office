using DevExpress.XtraEditors;

namespace Rizonesoft.Office.Settings
{
    /// <summary>
    /// Handles the geometry of a form.
    /// </summary>
    public static class FormGeometry
    {
        private const string Delimiter = "|";
        private const string NormalState = "Normal";
        private const string MaximizedState = "Maximized";

        /// <summary>
        /// Sets the geometry of a form based on a serialized string.
        /// </summary>
        public static void GeometryFromString(string windowGeometry, XtraForm form)
        {
            if (string.IsNullOrWhiteSpace(windowGeometry))
            {
                return;
            }

            var values = windowGeometry.Split(Delimiter);
            if (values.Length < 6)
            {
                throw new ArgumentException(@"Invalid geometry string", nameof(windowGeometry));
            }

            var windowState = values[4];
            if (!int.TryParse(values[0], out var x) ||
                !int.TryParse(values[1], out var y) ||
                !int.TryParse(values[2], out var width) ||
                !int.TryParse(values[3], out var height) ||
                !int.TryParse(values[5], out var screenIndex))
            {
                throw new ArgumentException(@"Invalid geometry string", nameof(windowGeometry));
            }

            var windowPoint = new Point(x, y);
            var windowSize = new Size(width, height);

            Screen? screen = screenIndex >= 0 && screenIndex < Screen.AllScreens.Length
                ? Screen.AllScreens[screenIndex]
                : Screen.PrimaryScreen;

            switch (windowState)
            {
                case NormalState:
                    ApplyNormalWindowState(form, windowPoint, windowSize, screen);
                    break;
                case MaximizedState:
                    ApplyMaximizedWindowState(form);
                    break;
                default:
                    throw new ArgumentException($@"Invalid window state {windowState}", nameof(windowGeometry));
            }
        }

        /// <summary>
        /// Serializes the geometry of a form to a string.
        /// </summary>
        public static string GeometryToString(XtraForm mainForm)
        {
            int screenIndex = Array.IndexOf(Screen.AllScreens, Screen.FromControl(mainForm));
            return $"{mainForm.Location.X}{Delimiter}{mainForm.Location.Y}{Delimiter}{mainForm.Size.Width}{Delimiter}{mainForm.Size.Height}{Delimiter}{mainForm.WindowState}{Delimiter}{screenIndex}";
        }

        private static void ApplyNormalWindowState(XtraForm form, Point location, Size size, Screen? screen)
        {
            if (screen != null && location.X + size.Width > screen.WorkingArea.Right)
            {
                location.X = screen.WorkingArea.Right - size.Width;
            }
            if (screen != null && location.Y + size.Height > screen.WorkingArea.Bottom)
            {
                location.Y = screen.WorkingArea.Bottom - size.Height;
            }
            if (screen != null && location.X < screen.WorkingArea.Left)
            {
                location.X = screen.WorkingArea.Left;
            }
            if (screen != null && location.Y < screen.WorkingArea.Top)
            {
                location.Y = screen.WorkingArea.Top;
            }

            form.Location = location;

            if (screen != null && size.Width > screen.WorkingArea.Width)
            {
                size.Width = screen.WorkingArea.Width;
            }
            if (screen != null && size.Height > screen.WorkingArea.Height)
            {
                size.Height = screen.WorkingArea.Height;
            }

            form.Size = size;
            form.StartPosition = FormStartPosition.Manual;
            form.WindowState = FormWindowState.Normal;
        }

        private static void ApplyMaximizedWindowState(XtraForm form)
        {
            form.Location = new Point(100, 100);
            form.StartPosition = FormStartPosition.Manual;
            form.WindowState = FormWindowState.Maximized;
        }
    }
}
