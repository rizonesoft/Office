using DevExpress.XtraSpellChecker;
using Rizonesoft.Office.Verbum.Forms;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Rizonesoft.Office.Verbum.Classes
{
    public class SpellCheckerExceptionHandler
    {
        readonly SpellChecker spellControl;
        public SpellCheckerExceptionHandler(SpellChecker spellControl)
        {
            this.spellControl = spellControl;
        }
        public void Install()
        {
            if (spellControl != null)
                spellControl.UnhandledException += OnSpellCheckerUnhandledException;
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


    }
}
