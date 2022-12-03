using DevExpress.XtraRichEdit.API.Native;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;

namespace HyperlinkClickExample.Forms
{
    public partial class SelectProductForm : DevExpress.XtraEditors.XtraForm
    {
        #region #Properties
        object editValue;
        DocumentRange range;
        public virtual object EditValue { get { return editValue; } }
        public DocumentRange Range { get { return range; }  set { range = value; } }
        #endregion #Properties
        public SelectProductForm()
        {
            InitializeComponent();
        }

        #region #PopulateListBox
        //Populate the ListBoxControl with items based on the custom list retrieved from the main form:
        private void PopulateListBox(List<string> list)
        {
            this.listBoxControl.Items.AddRange(list.ToArray());
            if (list.Count > 0)
                this.listBoxControl.SelectedIndex = 0;
        }
        public SelectProductForm(List<string> list) : this()
        {
            PopulateListBox(list);
        }
        #endregion #PopulateListBox

        #region #Events
        //Handle the MouseMove and MouseClick events to support item selection by using mouse:
        private void listBoxControl_MouseMove(object sender, MouseEventArgs e)
        {
            for (int i = 0; i < this.listBoxControl.ItemCount; i++)
            {
                Rectangle rect = this.listBoxControl.GetItemRectangle(i);
                if (rect.Contains(e.X, e.Y))
                {
                    this.listBoxControl.SelectedIndex = i;
                    break;
                }
            }
        }
        private void listBoxControl_MouseClick(object sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left || this.listBoxControl.SelectedIndex < 0)
                return;
            Rectangle rect = this.listBoxControl.GetItemRectangle(this.listBoxControl.SelectedIndex);
            if (!rect.Contains(e.X, e.Y))
                return;
            OnCommit();
        }
        //Handle the form KeyDown event to support keyboard navigation and item selection using the Enter key:
        private void SelectProductForm_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyData == Keys.Escape)
                Close();
            else if (e.KeyData == Keys.Enter)
                OnCommit();
        }
        protected virtual void OnCommit()
        {
            this.editValue = (string)this.listBoxControl.SelectedItem;
            if (onCommit != null)
                onCommit.Invoke(this, EventArgs.Empty);
            Close();
        }
        #endregion #Events

        #region #Commit
        EventHandler onCommit;
        public event EventHandler Commit { add { onCommit += value; } remove { onCommit -= value; } }
        #endregion #Commit
    }
}





