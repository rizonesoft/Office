using DevExpress.XtraSpellChecker;
using System;
using System.Windows.Forms;
using DevExpress.XtraEditors;

namespace Rizonesoft.Office.Verbum.Classes
{
    /// <summary>
    /// Handles exceptions for SpellChecker.
    /// </summary>
    public class SpellCheckerExceptionHandler
    {
        private readonly SpellChecker spellControl;

        /// <summary>
        /// Initializes a new instance of the <see cref="SpellCheckerExceptionHandler"/> class.
        /// </summary>
        /// <param name="spellControl">The SpellChecker to handle exceptions for.</param>
        /// <exception cref="ArgumentNullException">Thrown when spellControl is null.</exception>
        public SpellCheckerExceptionHandler(SpellChecker spellControl)
        {
            this.spellControl = spellControl ?? throw new ArgumentNullException(nameof(spellControl));
        }

        /// <summary>
        /// Installs the exception handler for the control.
        /// </summary>
        public void Install()
        {
            spellControl.UnhandledException += OnSpellCheckerUnhandledException;
        }

        /// <summary>
        /// Handles the UnhandledException event of the SpellChecker.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="SpellCheckerUnhandledExceptionEventArgs"/> instance containing the event data.</param>
        protected virtual void OnSpellCheckerUnhandledException(object sender, SpellCheckerUnhandledExceptionEventArgs e)
        {
            if (e.Exception == null) 
                return;

            var title = e.Exception is NotLoadedDictionaryException ? "Dictionary not Loaded!" : "Something went wrong!";
            XtraMessageBox.Show(e.Exception.Message, title, MessageBoxButtons.OK, MessageBoxIcon.Error);
            e.Handled = true;
        }
    }
}
