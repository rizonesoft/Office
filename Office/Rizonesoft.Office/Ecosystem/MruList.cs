using DevExpress.XtraBars;
using System.IO;
using Rizonesoft.Office.Utilities;
using Rizonesoft.Office.ErrorHandling;

namespace Rizonesoft.Office.Ecosystem
{
    /// <summary>
    /// Manages a list of Most Recently Used (MRU) files.
    /// </summary>
    public sealed class MruList
    {
        private readonly BarButtonItem[] mruBtnItems;
        private readonly List<FileInfo> fileInfos;
        private readonly int maxFiles;
        private readonly IMruRegistryHandler mruRegistryHandler;

        /// <summary>
        /// Event fired when a file is selected from the list.
        /// </summary>
        public event Action<string>? FileSelected;

        public MruList(BarLinksHolder popMenu, int numFiles, IMruRegistryHandler mruRegistryHandler)
        {
            this.mruRegistryHandler = mruRegistryHandler;
            maxFiles = numFiles;
            fileInfos = new List<FileInfo>();
            mruBtnItems = new BarButtonItem[maxFiles];

            for (var i = 0; i < maxFiles; i++)
            {
                mruBtnItems[i] = new BarButtonItem
                {
                    Visibility = BarItemVisibility.Never
                };
                mruBtnItems[i].ItemClick += MruFile_ItemClick;
                popMenu.ItemLinks.Add(mruBtnItems[i]);
            }
        }


        /// <summary>
        /// Initializes the list of MRU files.
        /// </summary>
        public void Initialize()
        {
            LoadFiles();
            ShowFiles();
        }

        private void LoadFiles()
        {
            string[] recentFiles = mruRegistryHandler.LoadFiles();

            foreach (var file in recentFiles)
            {
                fileInfos.Add(new FileInfo(file));
            }
        }

        /// <summary>
        /// Adds a file to the list.
        /// </summary>
        /// <param name="fileName">The name of the file to add.</param>
        public void AddFile(string fileName)
        {
            if (!File.Exists(fileName))
            {
                ShowFileNotFoundMessage(fileName);
                return;
            }

            var newFileInfo = new FileInfo(fileName);
            fileInfos.RemoveAll(file => file.FullName == newFileInfo.FullName);
            fileInfos.Insert(0, newFileInfo);
            if (fileInfos.Count > maxFiles)
            {
                fileInfos.RemoveAt(maxFiles);
            }

            ShowFiles();
            SaveFiles();
        }

        /// <summary>
        /// Removes a file from the list.
        /// </summary>
        /// <param name="fileName">The name of the file to remove.</param>
        public void RemoveFile(string fileName)
        {
            // Remove the file from the list of FileInfo objects.
            fileInfos.RemoveAll(file => file.FullName == fileName);
            // Show the updated list in the UI.
            ShowFiles();
            // Save the updated list to the registry.
            SaveFiles();
        }

        private void SaveFiles()
        {
            var filePaths = fileInfos.Select(fileInfo => fileInfo.FullName).ToList();
            mruRegistryHandler.SaveFiles(filePaths);
        }

        /// <summary>
        /// Shows the MRU files.
        /// </summary>
        public void ShowFiles()
        {
            for (var i = 0; i < maxFiles; i++)
            {
                if (i < fileInfos.Count)
                {
                    AssignProperties(mruBtnItems[i], fileInfos[i], i + 1);
                }
                else
                {
                    Hide(mruBtnItems[i]);
                }
            }
        }

        private static void AssignProperties(BarButtonItem item, FileInfo fileInfo, int index)
        {
            var extension = fileInfo.Extension;
            var iconUri = ImageResourceLoader.GetImageUriForExtension(extension);

            item.Caption = $@"&{index} {fileInfo.Name}";
            item.Visibility = BarItemVisibility.Always;
            item.Tag = fileInfo;
            item.ImageOptions.ImageUri.Uri = iconUri;
            item.ImageOptions.SvgImageSize = new Size(20, 20);
        }

        private static void Hide(BarButtonItem item)
        {
            item.Visibility = BarItemVisibility.Never;
        }

        private void MruFile_ItemClick(object sender, ItemClickEventArgs e)
        {
            var mruBtnItem = e.Item as BarButtonItem;
            var fileInfo = mruBtnItem?.Tag as FileInfo;

            if (fileInfo != null)
            {
                if (File.Exists(fileInfo.FullName))
                {
                    FileSelected?.Invoke(fileInfo.FullName);
                }
                else
                {
                    RemoveFile(fileInfo.FullName);
                    ShowFileNotFoundMessage(fileInfo.FullName);
                }
            }
        }

        private static void ShowFileNotFoundMessage(string fileName)
        {
            MessageBox.Show($"The file {fileName} could not be found.", "File not found", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}
