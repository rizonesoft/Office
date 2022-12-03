using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Reflection;
using DevExpress.XtraBars;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraRichEdit.Commands;
using DevExpress.XtraRichEdit.Localization;
using DevExpress.XtraRichEdit.UI;

namespace RichEditCustomInsertMergeFieldMenu {
    public class CustomInsertMergeFieldItem : BarButtonItem {
        private PopupMenu popupMenu;

        public CustomInsertMergeFieldItem() {
            InitializeItem();
        }

        public CustomInsertMergeFieldItem(BarManager manager)
            : base(manager, "") {
            InitializeItem();
        }

        public CustomInsertMergeFieldItem(string caption)
            : base(null, caption) {
            InitializeItem();
        }

        public CustomInsertMergeFieldItem(BarManager manager, string caption)
            : base(manager, caption) {
            InitializeItem();
        }

        private void InitializeItem() {
            this.popupMenu = new PopupMenu();
            this.popupMenu.BeforePopup += this.OnBeforePopup;
        }

        #region Properties
        [Browsable(false)]
        [EditorBrowsable(EditorBrowsableState.Never)]
        [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
        public override BarButtonStyle ButtonStyle { get { return BarButtonStyle.DropDown; } set { } }
        [Browsable(false)]
        [EditorBrowsable(EditorBrowsableState.Never)]
        [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
        public override PopupControl DropDownControl { get { return popupMenu; } set { } }
        [Browsable(false)]
        [EditorBrowsable(EditorBrowsableState.Never)]
        [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
        public override string Caption { get { return XtraRichEditLocalizer.Active.GetLocalizedString(XtraRichEditStringId.MenuCmd_InsertMergeField); } set { } }
        [Browsable(false)]
        [EditorBrowsable(EditorBrowsableState.Never)]
        [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
        public override Image Glyph { get { return Image.FromStream(Assembly.GetExecutingAssembly().GetManifestResourceStream("RichEditCustomInsertMergeFieldMenu.Images.InsertDataField_16x16.png")); } set { } }
        [Browsable(false)]
        [EditorBrowsable(EditorBrowsableState.Never)]
        [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
        public override Image LargeGlyph { get { return Image.FromStream(Assembly.GetExecutingAssembly().GetManifestResourceStream("RichEditCustomInsertMergeFieldMenu.Images.InsertDataField_32x32.png")); } set { } }
        private RichEditControl richEditControl;
        public RichEditControl RichEditControl { get { return richEditControl; } set { richEditControl = value; } }
        #endregion

        private void PopulatePopupMenu() {
            RichEditMailMergeOptions mailMergeOptions = RichEditControl.Options.MailMerge;
            DataBindingController mergeFieldsController = new DataBindingController(mailMergeOptions.DataSource, mailMergeOptions.DataMember);
            List<string> columnNames = mergeFieldsController.ColumnNames;
            Dictionary<string, BarSubItem> subItems = new Dictionary<string, BarSubItem>();

            for (int i = 0; i < columnNames.Count; i++) {
                string fullColumnName = columnNames[i];

                int dotIndex = fullColumnName.IndexOf('.');

                if (dotIndex == -1) {
                    InsertMergeFieldMenuItem item = new CustomInsertMergeFieldMenuItem(RichEditControl, new MergeFieldName(fullColumnName));
                    this.popupMenu.ItemLinks.Add(item);
                }
                else {
                    string groupName = fullColumnName.Substring(0, dotIndex);
                    string columnName = fullColumnName.Substring(groupName.Length + 1);

                    if (!subItems.ContainsKey(groupName)) {
                        BarSubItem subItem = new BarSubItem();
                        subItem.Caption = groupName;
                        subItems.Add(groupName, subItem);
                        this.popupMenu.ItemLinks.Add(subItem);
                    }

                    InsertMergeFieldMenuItem item = new CustomInsertMergeFieldMenuItem(RichEditControl, new MergeFieldName(fullColumnName, columnName));
                    subItems[groupName].ItemLinks.Add(item);
                }
            }
        }

        private void RefreshPopupMenu() {
            DeletePopupItems();
            if (RichEditControl != null)
                PopulatePopupMenu();
        }

        private void DeletePopupItems() {
            BarItemLinkCollection itemLinks = this.popupMenu.ItemLinks;
            this.popupMenu.BeginUpdate();
            try {
                while (itemLinks.Count > 0)
                    itemLinks[0].Item.Dispose();
            }
            finally {
                this.popupMenu.EndUpdate();
            }
        }

        private void OnBeforePopup(object sender, CancelEventArgs e) {
            RefreshPopupMenu();
        }

        protected override void OnClick(BarItemLink link) {
            if (RichEditControl != null)
                RichEditControl.CreateCommand(RichEditCommandId.ShowInsertMergeFieldForm).Execute();
        }

        protected override void OnManagerChanged() {
            base.OnManagerChanged();
            this.popupMenu.Manager = this.Manager;
        }

        #region IDisposable implementation
        protected override void Dispose(bool disposing) {
            base.Dispose(disposing);
            if (disposing) {
                if (popupMenu != null) {
                    DeletePopupItems();
                    popupMenu.Dispose();
                    popupMenu = null;
                }
            }
        }
        #endregion
    }

    public class CustomInsertMergeFieldMenuItem : InsertMergeFieldMenuItem {
        private RichEditControl control;
        private string fieldName;

        public CustomInsertMergeFieldMenuItem(RichEditControl control, MergeFieldName mergeFieldName)
            : base(control, mergeFieldName) {
            DevExpress.Utils.Guard.ArgumentNotNull(control, "control");
            this.control = control;
            this.fieldName = mergeFieldName.Name;
        }

        protected override void OnClick(BarItemLink link) {
            control.Document.Fields.Create(control.Document.CaretPosition, string.Format(" MERGEFIELD {0} ", this.fieldName));
        }
    }
}