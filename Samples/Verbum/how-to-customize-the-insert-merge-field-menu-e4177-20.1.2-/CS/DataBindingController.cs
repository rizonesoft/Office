using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Windows.Forms;

namespace RichEditCustomInsertMergeFieldMenu {
    public class DataBindingController {
        private static BindingContext bindingContext = new BindingContext();
        private object dataSource;
        private string dataMember;
        private BindingManagerBase bindingManager = null;
        private PropertyDescriptorCollection itemProperties = null;

        public DataBindingController(object dataSource, string dataMember) {
            this.dataSource = dataSource;
            this.dataMember = dataMember;
            InitializeBindingManagerAndItemProperties();
        }

        private void InitializeBindingManagerAndItemProperties() {
            if (dataSource != null) {
                if (dataMember.Length > 0)
                    bindingManager = bindingContext[dataSource, dataMember];
                else
                    bindingManager = bindingContext[dataSource];
            }
            if (bindingManager != null)
                itemProperties = bindingManager.GetItemProperties();
        }

        public int ItemsCount {
            get {
                return (bindingManager != null) ? bindingManager.Count : 0;
            }
        }

        public List<string> ColumnNames {
            get {
                List<string> list = new List<string>();

                if (itemProperties != null) {
                    int count = itemProperties.Count;
                    for (int i = 0; i < count; i++) {
                        list.Add(itemProperties[i].Name);
                    }
                }

                return list;
            }
        }

        public PropertyDescriptor GetColumnInfo(string columnName) {
            if (itemProperties != null) {
                PropertyDescriptor prop = itemProperties.Find(columnName, false);

                if (prop == null)
                    throw new ArgumentException(string.Format("'{0}' column does not exist", columnName));

                return (itemProperties != null ? itemProperties[columnName] : null);
            }

            return null;
        }

        public object GetRowValue(string columnName, int rowIndex) {
            if (bindingManager != null && itemProperties != null) {
                PropertyDescriptor prop = itemProperties.Find(columnName, false);

                if (prop == null)
                    throw new ArgumentException(string.Format("'{0}' column does not exist", columnName));

                if (bindingManager is CurrencyManager)
                    return prop.GetValue(((CurrencyManager)bindingManager).List[rowIndex]);
                else {
                    if (rowIndex != 0)
                        throw new ArgumentOutOfRangeException("rowIndex");
                    return prop.GetValue(((PropertyManager)bindingManager).Current);
                }
            }

            return null;
        }
    }
}
