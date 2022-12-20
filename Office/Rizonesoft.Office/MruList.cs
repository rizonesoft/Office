using DevExpress.XtraBars;
using System.Collections.Generic;
using System.IO;

namespace Rizonesoft.Office
{
    public class MruList
    {

        private string SaveMRUPath;
        private string MruSection;
        private int iFiles;
        private List<FileInfo> fileInfos;

        private PopupMenu mruMenu;
        private BarButtonItem[] mruBtnItems;

        public delegate void FileSelectedEventHandler(string fileName);
        public event FileSelectedEventHandler FileSelected;


        public MruList(string mruKey, PopupMenu popMenu, int numFiles, string saveMRUPath)
        {

            MruSection = mruKey;
            mruMenu = popMenu;
            iFiles = numFiles;
            SaveMRUPath = saveMRUPath;
            fileInfos = new List<FileInfo>();

            mruBtnItems = new BarButtonItem[iFiles + 1];
            for (int i = 0; i < iFiles; i++)
            {
                mruBtnItems[i] = new BarButtonItem();
                mruBtnItems[i].ImageOptions.ImageUri.Uri = "richedit/columnsone";
                mruBtnItems[i].Visibility = BarItemVisibility.Never;
                mruMenu.ItemLinks.Add(mruBtnItems[i]); 
            }

            LoadFiles();
            ShowFiles();
        }

        private void LoadFiles()
        {

            for (int i = 0; i < iFiles; i++)
            {
                string fileName = Settings.Settings.GetSetting(SaveMRUPath, "FilePath" + i.ToString(), "");

                if (string.IsNullOrWhiteSpace(fileName))
                {
                    continue;
                }
                fileInfos.Add(new FileInfo(fileName));
            }
        }

        private void SaveFiles()
        {
            for (int i = 0; i < iFiles; i++)
            {
                Settings.Settings.DeleteSetting(SaveMRUPath, "FilePath" + i.ToString());
            }

            int index = 0;
            foreach (FileInfo fileInfo in fileInfos)
            {
                Settings.Settings.SaveSetting(SaveMRUPath, "FilePath" + index.ToString(), fileInfo.FullName);
                index++;
            }
        }

        private void RemoveFileInfo(string fileName)
        {
            for (int i = fileInfos.Count - 1; i >= 0; i--)
            {
                if (fileInfos[i].FullName == fileName)
                    fileInfos.RemoveAt(i);
            }
        }

        public void AddFile(string fileName)
        {
            RemoveFileInfo(fileName);
            fileInfos.Insert(0, new FileInfo(fileName));
            if (fileInfos.Count > iFiles)
            {
                fileInfos.RemoveAt(iFiles);
            }
            ShowFiles();
            SaveFiles();
        }

        public void RemoveFile(string fileName)
        {
            RemoveFileInfo(fileName);
            ShowFiles();
            SaveFiles();
        }

        private void ShowFiles()
        {
            for (int i = 0; i < fileInfos.Count; i++)
            {
                mruBtnItems[i].Caption = string.Format("&{0} {1}", i + 1, fileInfos[i].Name);
                mruBtnItems[i].Visibility = BarItemVisibility.Always;
                mruBtnItems[i].Tag = fileInfos[i];
                mruBtnItems[i].ItemClick -= mruFile_ItemClick;
                mruBtnItems[i].ItemClick += new DevExpress.XtraBars.ItemClickEventHandler(mruFile_ItemClick);
            }
            for (int i = fileInfos.Count; i < iFiles; i++)
            {
                mruBtnItems[i].Visibility = BarItemVisibility.Never;
                mruBtnItems[i].ItemClick -= mruFile_ItemClick;
            }
        }

        private void mruFile_ItemClick(object sender, ItemClickEventArgs e)
        {
            if (FileSelected != null)
            {
                BarButtonItem mruBtnItem = e.Item as BarButtonItem;
                FileInfo fileInfo = mruBtnItem.Tag as FileInfo;
                FileSelected(fileInfo.FullName);
            }
        }

    }

}
