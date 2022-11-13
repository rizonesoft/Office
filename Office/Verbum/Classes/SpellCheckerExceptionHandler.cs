using DevExpress.XtraSpellChecker;
using System;

namespace Rizonesoft.Office.Verbum.Classes
{

    public class SpellCheckerExceptionHandler
    {

        internal readonly SpellChecker spellControl;

        public SpellCheckerExceptionHandler(SpellChecker spellControl)
        {
            this.spellControl = spellControl;
        }

        protected virtual void OnSpellCheckerUnhandledException(object sender, SpellCheckerUnhandledExceptionEventArgs e)
        {
            try
            {
                if (e.Exception != null)
                    throw e.Exception;
            }
            catch (NotLoadedDictionaryException ex)
            {
                new ExceptionForm(ex).ShowDialog();
                e.Handled = true;
            }
            catch (Exception ex)
            {
                new ExceptionForm(ex).ShowDialog();
                e.Handled = true;
            }
        }

        public void Install()
        {
            if (spellControl != null)
            {
                spellControl.UnhandledException += OnSpellCheckerUnhandledException;
            }
        }

    }

}
