namespace Rizonesoft.Office.Interprocess
{
    using System;
    using System.IO;
    using System.Collections;
    using System.Windows.Forms;
    using System.Runtime.InteropServices;
    using Newtonsoft.Json;


    public delegate void DataReceivedEventHandler(object sender, DataReceivedEventArgs e);

    public sealed class CopyData : NativeWindow, IDisposable
    {
        public event DataReceivedEventHandler? DataReceived;

        [StructLayout(LayoutKind.Sequential)]

        private readonly struct CopyDataStruct
        {
            private readonly nint dwData;
            public readonly int cbData;
            public readonly nint lpData;
        }

        private const int WmCopydata = 0x4A;
        private const int WmDestroy = 0x2;
        private bool disposed;

        protected override void WndProc(ref Message m)
        {
            switch (m.Msg)
            {
                case WmCopydata:
                {
                    var cds = (CopyDataStruct)(Marshal.PtrToStructure(m.LParam, typeof(CopyDataStruct)) ??
                                               throw new InvalidOperationException());
                    if (cds.cbData > 0)
                    {
                        var data = new byte[cds.cbData];
                        Marshal.Copy(cds.lpData, data, 0, cds.cbData);
                        var stream = new MemoryStream(data);
                        var serializer = new JsonSerializer();
                        using var reader = new StreamReader(stream);
                        using var jsonReader = new JsonTextReader(reader);
                        var cdo = serializer.Deserialize<CopyDataObjectData>(jsonReader);
                        if (Channels != null && Channels.Contains(cdo?.Channel))
                        {
                            if (cdo != null)
                            {
                                var d = new DataReceivedEventArgs(cdo.Channel, cdo.Data, cdo.Sent);
                                OnDataReceived(d);
                            }

                            m.Result = 1;
                        }
                    }

                    break;
                }
                case WmDestroy:
                {
                    Channels?.OnHandleChange();
                    base.OnHandleChange();
                    break;
                }
            }

            base.WndProc(ref m);

        }

        private void OnDataReceived(DataReceivedEventArgs e)
        {
            DataReceived?.Invoke(this, e);
        }

        protected override void OnHandleChange()
        {
            base.OnHandleChange();
            Channels?.OnHandleChange();
        }

        public CopyDataChannels? Channels { get; private set; }

        public void Dispose()
        {
            if (disposed) return;
            disposed = true;
            Channels?.Clear();
            Channels = null;
            GC.SuppressFinalize(this);
        }

        public CopyData()
        {
            Channels = new CopyDataChannels(this);
        }

        ~CopyData()
        {
            Dispose();
        }
    }


    public sealed class DataReceivedEventArgs
    {
        public string? ChannelName { get; }
        public object? Data { get; }
        public DateTime Sent { get; }
        public DateTime Received { get; }

        public DataReceivedEventArgs(string? channelName, object? data, DateTime sent)
        {
            ChannelName = channelName;
            Data = data;
            Sent = sent;
            Received = DateTime.UtcNow;
        }
    }

    public sealed class CopyDataChannels : DictionaryBase
    {
        private readonly NativeWindow owner;

        public CopyDataChannel? this[int index] => Dictionary.Values.Cast<CopyDataChannel>().ElementAtOrDefault(index);
        public CopyDataChannel? this[string channelName] => Dictionary[channelName] as CopyDataChannel;

        public void Add(string? channelName)
        {
            var cdc = new CopyDataChannel(owner, channelName);
            if (channelName != null) Dictionary.Add(channelName, cdc);
        }

        public void Remove(string channelName)
        {
            var channel = Dictionary[channelName] as CopyDataChannel;
            channel?.Dispose();
            Dictionary.Remove(channelName);
        }

        internal bool Contains(string? channelName)
        {
            return channelName != null && Dictionary.Contains(channelName);
        }

        protected override void OnClear()
        {
            foreach (CopyDataChannel cdc in Dictionary.Values)
            {
                cdc.Dispose();
            }
            base.OnClear();
        }

        protected override void OnRemoveComplete(object? key, object? data)
        {
            if (data is not CopyDataChannel channel) return;
            channel.Dispose();
            if (key != null) OnRemove(key, data);
        }

        internal void OnHandleChange()
        {
            foreach (CopyDataChannel cdc in Dictionary.Values)
            {
                cdc.OnHandleChange();
            }
        }

        internal CopyDataChannels(NativeWindow owner)
        {
            this.owner = owner;
        }
    }


    public sealed partial class CopyDataChannel : IDisposable
    {
        [LibraryImport("user32", EntryPoint = "GetPropW", StringMarshalling = StringMarshalling.Utf16)]
        private static partial int GetProp(nint hwnd, string? lpString);
        [LibraryImport("user32", EntryPoint = "SetPropW", StringMarshalling = StringMarshalling.Utf16)]
        private static partial void SetProp(IntPtr hwnd, string? lpString, int hData);
        [LibraryImport("user32", EntryPoint = "RemovePropW", StringMarshalling = StringMarshalling.Utf16)]
        private static partial void RemoveProp(IntPtr hwnd, string? lpString);
        [LibraryImport("user32", EntryPoint = "SendMessageW")]
        private static partial int SendMessage(nint hwnd, int wMsg, int wParam, ref CopyDataStruct lParam);

        [StructLayout(LayoutKind.Sequential)]
        private struct CopyDataStruct
        {
            public nint dwData;
            public int cbData;
            public nint lpData;
        }

        private const int WmCopydata = 0x4A;
        private bool disposed;
        private readonly NativeWindow owner;
        private bool recreateChannel;

        private string? ChannelName { get; set; }


        public int Send(object? obj)
        {
            var recipients = 0;

            if (disposed)
            {
                throw new InvalidOperationException("Object has been disposed");
            }

            if (recreateChannel)
            {
                AddChannel();
            }

            var cdo = new CopyDataObjectData(obj, ChannelName);
            var serializer = new JsonSerializer();
            var stream = new MemoryStream();
            using (var writer = new StreamWriter(stream, leaveOpen: true))
            using (var jsonWriter = new JsonTextWriter(writer))
            {
                serializer.Serialize(jsonWriter, cdo);
            }
            stream.Flush();

            var dataSize = (int)stream.Length;
            if (dataSize > 0)
            {
                var data = new byte[dataSize];
                stream.Seek(0, SeekOrigin.Begin);
                _ = stream.Read(data, 0, dataSize);
                var ptrData = Marshal.AllocCoTaskMem(dataSize);
                Marshal.Copy(data, 0, ptrData, dataSize);
                var ew = new EnumWindows();
                ew.GetWindows();

                foreach (EnumWindowsItem window in ew.Items)
                {
                    if (!window.Handle.Equals(owner.Handle))
                    {
                        if (GetProp(window.Handle, ChannelName) != 0)
                        {
                            var cds = new CopyDataStruct();
                            cds.cbData = dataSize;
                            cds.dwData = nint.Zero;
                            cds.lpData = ptrData;
                            // ReSharper disable once UnusedVariable
                            var res = SendMessage(window.Handle, WmCopydata, (int)owner.Handle, ref cds);
                            recipients += Marshal.GetLastWin32Error() == 0 ? 1 : 0;
                        }
                    }
                }
                Marshal.FreeCoTaskMem(ptrData);
            }
            stream.Close();

            return recipients;
        }

        private void AddChannel()
        {
            SetProp(owner.Handle, ChannelName, (int)owner.Handle);

        }
        private void RemoveChannel()
        {
            RemoveProp(owner.Handle, ChannelName);
        }

        internal void OnHandleChange()
        {
            RemoveChannel();
            recreateChannel = true;
        }

        public void Dispose()
        {
            if (disposed) return;
            if (ChannelName is { Length: > 0 })
            {
                RemoveChannel();
            }
            ChannelName = "";
            disposed = true;
            GC.SuppressFinalize(this);
        }

        internal CopyDataChannel(NativeWindow owner, string? channelName)
        {
            this.owner = owner;
            this.ChannelName = channelName;
            AddChannel();
        }

        ~CopyDataChannel()
        {
            Dispose();
        }
    }


    [Serializable()]
    internal class CopyDataObjectData
    {
        /// <summary>
        /// The Object to copy.  Must be Serializable.
        /// </summary>
        public object? Data;
        /// <summary>
        /// The date and time this object was sent.
        /// </summary>
        public DateTime Sent;
        /// <summary>
        /// The name of the channel this object is being sent on
        /// </summary>
        public string? Channel;

        /// <summary>
        /// Constructs a new instance of this object
        /// </summary>
        /// <param name="data">The data to copy</param>
        /// <param name="channel">The channel name to send on</param>
        /// <exception cref="ArgumentException">If data is not serializable.</exception>
        public CopyDataObjectData(object? data, string? channel)
        {
            Data = data;
            if (data != null && !data.GetType().IsSerializable)
            {
                throw new ArgumentException(@"Data object must be serializable.", "data");
            }
            Channel = channel;
            Sent = DateTime.Now;
        }
    }
}