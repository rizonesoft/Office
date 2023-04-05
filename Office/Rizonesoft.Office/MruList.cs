namespace Rizonesoft.Office
{
    using DevExpress.XtraBars;
    using System.Collections.Generic;
    using System.IO;

    public sealed class MruList
    {

        private readonly string saveMruPath;
        //private string mruSection;
        private readonly int iFiles;
        private readonly List<FileInfo> fileInfos;
        private readonly BarButtonItem[] mruBtnItems;

        public delegate void FileSelectedEventHandler(string fileName);
        public event FileSelectedEventHandler? FileSelected;


        public MruList(string mruKey, BarLinksHolder popMenu, int numFiles, string saveMruPath)
        {
            //mruSection = mruKey;
            iFiles = numFiles;
            this.saveMruPath = saveMruPath;
            fileInfos = new List<FileInfo>();

            mruBtnItems = new BarButtonItem[iFiles + 1];
            for (var i = 0; i < iFiles; i++)
            {
                mruBtnItems[i] = new BarButtonItem();
                mruBtnItems[i].ImageOptions.ImageUri.Uri = "richedit/columnsone";
                mruBtnItems[i].Visibility = BarItemVisibility.Never;
                popMenu.ItemLinks.Add(mruBtnItems[i]);
            }

            LoadFiles();
            ShowFiles();
        }

        private void LoadFiles()
        {

            for (var i = 0; i < iFiles; i++)
            {
                var fileName = Settings.Settings.GetSetting(saveMruPath, "FilePath" + i.ToString(), "");
                if (string.IsNullOrWhiteSpace(fileName))
                {
                    continue;
                }
                fileInfos.Add(new FileInfo(fileName));
            }
        }

        private void SaveFiles()
        {
            for (var i = 0; i < iFiles; i++)
            {
                Settings.Settings.DeleteSetting(saveMruPath, "FilePath" + i.ToString());
            }

            var index = 0;
            foreach (var fileInfo in fileInfos)
            {
                Settings.Settings.SaveSetting(saveMruPath, "FilePath" + index.ToString(), fileInfo.FullName);
                index++;
            }
        }

        private void RemoveFileInfo(string fileName)
        {
            for (var i = fileInfos.Count - 1; i >= 0; i--)
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
            for (var i = 0; i < fileInfos.Count; i++)
            {
                mruBtnItems[i].Caption = $@"&{i + 1} {fileInfos[i].Name}";
                mruBtnItems[i].Visibility = BarItemVisibility.Always;
                mruBtnItems[i].Tag = fileInfos[i];
                mruBtnItems[i].ItemClick -= MruFile_ItemClick;
                mruBtnItems[i].ItemClick += MruFile_ItemClick;
            }
            for (var i = fileInfos.Count; i < iFiles; i++)
            {
                mruBtnItems[i].Visibility = BarItemVisibility.Never;
                mruBtnItems[i].ItemClick -= MruFile_ItemClick;
            }
        }

        private void MruFile_ItemClick(object sender, ItemClickEventArgs e)
        {
            if (FileSelected == null) return;
            if (e.Item != null)
            {
                if (e.Item is not BarButtonItem mruBtnItem) return;
                if (mruBtnItem.Tag is FileInfo fileInfo)
                {
                    FileSelected(fileInfo.FullName);
                }
            }
            else
            {
                throw new NullReferenceException("DevExpress.XtraBars.ItemClickEventArgs (e) is null.");
            }
        }

    }

}
