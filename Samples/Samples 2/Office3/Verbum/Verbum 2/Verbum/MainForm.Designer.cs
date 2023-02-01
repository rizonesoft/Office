namespace Rizonesoft.Verbum
{
    partial class MainForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            DevExpress.XtraSplashScreen.SplashScreenManager splashScreenMan = new DevExpress.XtraSplashScreen.SplashScreenManager(this, null, true, true);
            this.coreDictionaryStorage = new DevExpress.XtraSpellChecker.SharedDictionaryStorage(this.components);
            this.dictionariesWorker = new System.ComponentModel.BackgroundWorker();
            this.timerMemory = new System.Windows.Forms.Timer(this.components);
            this.SuspendLayout();
            // 
            // dictionariesWorker
            // 
            this.dictionariesWorker.DoWork += new System.ComponentModel.DoWorkEventHandler(this.dictionariesWorker_DoWork);
            this.dictionariesWorker.RunWorkerCompleted += new System.ComponentModel.RunWorkerCompletedEventHandler(this.dictionariesWorker_RunWorkerCompleted);
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(44, 22);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "MainForm";
            this.Opacity = 0D;
            this.ShowIcon = false;
            this.ShowInTaskbar = false;
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.CoreForm_FormClosing);
            this.ResumeLayout(false);

        }

        #endregion

        private DevExpress.XtraSpellChecker.SharedDictionaryStorage coreDictionaryStorage;
        private System.ComponentModel.BackgroundWorker dictionariesWorker;
        private System.Windows.Forms.Timer timerMemory;
    }
}
