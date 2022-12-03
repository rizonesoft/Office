using System;
using System.Collections.Generic;
using System.Text;
using DevExpress.XtraEditors;
using DevExpress.Services;
using System.Windows.Forms;
using System.Drawing;

namespace ProgressIndicator
{
    #region #myprogressindicator
    class MyProgressIndicatorService : IProgressIndicationService
    {
        private ProgressBarControl _Indicator;
        public ProgressBarControl Indicator
        {
            get { return _Indicator; }
            set { _Indicator = value; }
        }

        public MyProgressIndicatorService(IServiceProvider provider, ProgressBarControl indicator)
        {
            _Indicator = indicator;
        }
        
        #region IProgressIndicationService Members

        void IProgressIndicationService.Begin(string displayName, int minProgress, int maxProgress, int currentProgress)
        {
            _Indicator.Properties.Minimum = minProgress;
            _Indicator.Properties.Maximum = maxProgress;
            _Indicator.Properties.ShowTitle = true;
            _Indicator.EditValue = currentProgress;
            _Indicator.Refresh();
            _Indicator.Show();            
        }

        void IProgressIndicationService.End()
        {
            _Indicator.Refresh();
            _Indicator.Hide();
        }

        void IProgressIndicationService.SetProgress(int currentProgress)
        {
            _Indicator.EditValue = currentProgress;
            _Indicator.Refresh();
        }
        #endregion
    }
#endregion #myprogressindicatorsindicator
}
