using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
using DevExpress.XtraRichEdit;
using DevExpress.XtraRichEdit.API.Native;
using DevExpress.XtraTreeList.Nodes;

namespace RichEditControlEventViewer
{
    public partial class Form1 : DevExpress.XtraBars.Ribbon.RibbonForm
    {
        #region Fields
        const string documentName = "Grimm.docx";
        List<RichEditEventHooker> hooks;
        #endregion

        public Form1()
        {
            hooks = new List<RichEditEventHooker>();
            InitializeComponent();
            PrepareContent();
            EnumerateEvents();
            checkAllEdit.CheckState = CheckState.Checked;
            UnCheckCustomDrawEvents();
        }

        #region static helper functions
        static int SortHooksByName(RichEditEventHooker arg1, RichEditEventHooker arg2)
        {
            return arg1.Name.CompareTo(arg2.Name);
        }
        #endregion

        void EnumerateEvents()
        {
            Type controlType = richEditControl1.GetType();
            EventInfo[] events = controlType.GetEvents(BindingFlags.Instance | BindingFlags.Public | BindingFlags.DeclaredOnly);
            foreach (EventInfo item in events)
            {
                string eventName = item.Name;
                if (eventName == "AutoCorrect")
                    hooks.Add(new AutoCorrectEventHooker(eventName, this));
                else 
                    hooks.Add(new RichEditEventHooker(eventName, this));
            }
            hooks.Sort(SortHooksByName);
            for (int i = 0; i < hooks.Count; ++i)
            {
                string eventName = hooks[i].Name;
                eventsCheckedListBox.Items.Add(i, eventName);
            }
        }

        void PrepareContent()
        {
            Document doc = richEditControl1.Document;
            richEditControl1.BeginUpdate();
            try
            {
                richEditControl1.LoadDocument(documentName);
            }
            finally
            {
                richEditControl1.EndUpdate();
            }
        }

        string GetEventParameter(PropertyInfo item, object value)
        {
            StringBuilder strBuilder = new StringBuilder();
            strBuilder.Append(item.Name);
            if (item.PropertyType == typeof(string))
            {
                strBuilder.Append("=\'");
                strBuilder.Append(value);
                strBuilder.Append('\'');
            }
            else
            {
                strBuilder.Append('=');
                strBuilder.Append(value);
            }
            return strBuilder.ToString();
        }

        public void InitializeEventLogger(string eventName, object sender, EventArgs args)
        {
            Type argsType = args.GetType();
            string name = eventName;
            string argsTypeName = argsType.Name;
            PropertyInfo[] propInfoArray = argsType.GetProperties();
            TreeListNode rootListNode = null;
            TreeListNode firstLevelNode = loggerControl.AppendNode(new object[] { name, argsTypeName }, rootListNode);
            foreach (PropertyInfo item in propInfoArray)
            {
                string value = GetEventParameter(item, item.GetValue(args, null));
                TreeListNode secondLevelNode = loggerControl.AppendNode(new object[] { "", "", value }, firstLevelNode);
            }
            if (appendExpandedBox.Checked && (propInfoArray.Length > 0))
                firstLevelNode.ExpandAll();
            loggerControl.MakeNodeVisible(firstLevelNode);
        }

        public void InitializeAutoCorrectEventLogger(string eventName, object sender, AutoCorrectEventArgs args)
        {
            args.AutoCorrectInfo = null;
            InitializeEventLogger(eventName, sender, args);
        }
        
        #region FormControls
        void eventsCheckedListBox_ItemCheck(object sender, DevExpress.XtraEditors.Controls.ItemCheckEventArgs e)
        {
            int itemIndex = e.Index;
            bool state = e.State == CheckState.Checked;
            int hookIndex = Convert.ToInt32(eventsCheckedListBox.Items[itemIndex].Value);
            if (state)
                hooks[hookIndex].HookEvent(richEditControl1);
            else
                hooks[hookIndex].UnhookEvent(richEditControl1);
        }

        void checkAllEdit_CheckStateChanged(object sender, EventArgs e)
        {
            CheckState state = checkAllEdit.CheckState;
            switch (state)
            {
                case CheckState.Checked:
                    eventsCheckedListBox.CheckAll();
                    break;
                case CheckState.Unchecked:
                    eventsCheckedListBox.UnCheckAll();
                    break;
            }
        }

        void expandButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            loggerControl.ExpandAll();
        }

        void collapseButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            loggerControl.CollapseAll();
        }

        void clearButtonItem_ItemClick(object sender, DevExpress.XtraBars.ItemClickEventArgs e)
        {
            loggerControl.ClearNodes();
        }

        private void UnCheckCustomDrawEvents()
        {
            for (int i = 0; i < eventsCheckedListBox.Items.Count; ++i)
            {
                if (eventsCheckedListBox.Items[i].Description.Contains("Draw"))
                    eventsCheckedListBox.Items[i].CheckState = CheckState.Unchecked;
            }
        }
        #endregion FormControls
    }
}
