using System.IO;

namespace Rizonesoft.Office.UI
{
    /// <summary>
    /// Helper class for managing child document forms.
    /// </summary>
    public static class ChildDocHelper
    {
        /// <summary>
        /// Sets the caption of a child document form.
        /// </summary>
        /// <param name="fileName">The file name to use as the caption.</param>
        /// <param name="childDocForm">The child document form whose caption to set.</param>
        /// <exception cref="ArgumentException">Thrown when fileName is null or empty.</exception>
        public static void SetDocumentCaption(string fileName, Control childDocForm)
        {
            if (string.IsNullOrEmpty(fileName))
            {
                throw new ArgumentException($@"{nameof(fileName)} cannot be null or empty.", nameof(fileName));
            }

            var fileCaption = Path.GetFileName(fileName);
            childDocForm.Text = fileCaption.Length > 28 ? $"{fileCaption[..28]}..." : fileCaption;
        }
    }
}