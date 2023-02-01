﻿using System;
using System.IO;
using System.Collections;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using System.Runtime.Serialization.Formatters.Binary;

namespace Rizonesoft.Office.Verbum.Classes
{
    public delegate void DataReceivedEventHandler(object sender, DataReceivedEventArgs e);

    /// <summary>
    /// A class which wraps using Windows native WM_COPYDATA
    /// message to send interprocess data between applications.
    /// This is a simple technique for interprocess data sends
    /// using Windows.  The alternative to this is to use
    /// Remoting, which requires a network card and a way
    /// to register the Remoting name of an object so it
    /// can be read by other applications.
    /// </summary>
    public class CopyData : NativeWindow, IDisposable
    {
        /// <summary>
        /// Event raised when data is received on any of the channels 
        /// this class is subscribed to.
        /// </summary>
        public event DataReceivedEventHandler DataReceived;

        [StructLayout(LayoutKind.Sequential)]
        private struct COPYDATASTRUCT
        {
            public IntPtr dwData;
            public int cbData;
            public IntPtr lpData;
        }

        private const int WM_COPYDATA = 0x4A;
        private const int WM_DESTROY = 0x2;

        #region Member Variables
        private CopyDataChannels channels = null;
        private bool disposed = false;
        #endregion

        /// <summary>
        /// Override for a form's Window Procedure to handle WM_COPYDATA
        /// messages sent by other instances of this class.
        /// </summary>
        /// <param name="m">The Windows Message information.</param>
        protected override void WndProc(ref System.Windows.Forms.Message m)
        {
            if (m.Msg == WM_COPYDATA)
            {
                COPYDATASTRUCT cds = new COPYDATASTRUCT();
                cds = (COPYDATASTRUCT)Marshal.PtrToStructure(m.LParam, typeof(COPYDATASTRUCT));
                if (cds.cbData > 0)
                {
                    byte[] data = new byte[cds.cbData];
                    Marshal.Copy(cds.lpData, data, 0, cds.cbData);
                    MemoryStream stream = new MemoryStream(data);
                    BinaryFormatter b = new BinaryFormatter();
                    CopyDataObjectData cdo = (CopyDataObjectData)b.Deserialize(stream);

                    if (channels.Contains(cdo.Channel))
                    {
                        DataReceivedEventArgs d = new DataReceivedEventArgs(cdo.Channel, cdo.Data, cdo.Sent);
                        OnDataReceived(d);
                        m.Result = (IntPtr)1;
                    }
                }
            }
            else if (m.Msg == WM_DESTROY)
            {
                // WM_DESTROY fires before OnHandleChanged and is
                // a better place to ensure that we've cleared 
                // everything up.
                channels.OnHandleChange();
                base.OnHandleChange();
            }
            base.WndProc(ref m);
        }

        /// <summary>
        /// Raises the DataReceived event from this class.
        /// </summary>
        /// <param name="e">The data which has been received.</param>
        protected void OnDataReceived(DataReceivedEventArgs e)
        {
            DataReceived(this, e);
        }

        /// <summary>
        /// If the form's handle changes, the properties associated
        /// with the window need to be cleared up. This override ensures
        /// that it is done.  Note that the CopyData class will then
        /// stop responding to events and it should be recreated once
        /// the new handle has been assigned.
        /// </summary>
        protected override void OnHandleChange()
        {
            // need to clear up everything we had set.
            channels.OnHandleChange();
            base.OnHandleChange();
        }

        /// <summary>
        /// Gets the collection of channels.
        /// </summary>
        public CopyDataChannels Channels
        {
            get
            {
                return this.channels;
            }
        }

        /// <summary>
        /// Clears up any resources associated with this object.
        /// </summary>
        public void Dispose()
        {
            if (!disposed)
            {
                channels.Clear();
                channels = null;
                disposed = true;
                GC.SuppressFinalize(this);
            }
        }

        /// <summary>
        /// Constructs a new instance of the CopyData class
        /// </summary>
        public CopyData()
        {
            channels = new CopyDataChannels(this);
        }

        /// <summary>
        /// Finalises a CopyData class which has not been disposed.
        /// There may be a minor resource leak if this class is finalised
        /// after the form it is associated with.
        /// </summary>
        ~CopyData()
        {
            Dispose();
        }
    }

    /// <summary>
    /// Contains data and other information associated with data
    /// which has been sent from another application.
    /// </summary>
    public class DataReceivedEventArgs
    {
        private string channelName = "";
        private object data = null;
        private DateTime sent;
        private DateTime received;

        /// <summary>
        /// Gets the channel name that this data was sent on.
        /// </summary>
        public string ChannelName
        {
            get
            {
                return this.channelName;
            }
        }
        /// <summary>
        /// Gets the data object which was sent.
        /// </summary>
        public Object Data
        {
            get
            {
                return this.data;
            }
        }
        /// <summary>
        /// Gets the date and time which at the data was sent
        /// by the sending application.
        /// </summary>
        public DateTime Sent
        {
            get
            {
                return this.sent;
            }
        }
        /// <summary>
        /// Gets the date and time which this data item as
        /// received.
        /// </summary>
        public DateTime Received
        {
            get
            {
                return this.received;
            }
        }
        /// <summary>
        /// Constructs an instance of this class.
        /// </summary>
        /// <param name="channelName">The channel that the data was received from</param>
        /// <param name="data">The data which was sent</param>
        /// <param name="sent">The date and time the data was sent</param>
        internal DataReceivedEventArgs(string channelName, object data, DateTime sent)
        {
            this.channelName = channelName;
            this.data = data;
            this.sent = sent;
            this.received = DateTime.Now;
        }
    }

    /// <summary>
    /// A strongly-typed collection of channels associated with the CopyData
    /// class.
    /// </summary>
    public class CopyDataChannels : DictionaryBase
    {
        private NativeWindow owner = null;

        /// <summary>
        /// Returns an enumerator for each of the CopyDataChannel objects
        /// within this collection.
        /// </summary>
        /// <returns>An enumerator for each of the CopyDataChannel objects
        /// within this collection.</returns>
        public new System.Collections.IEnumerator GetEnumerator()
        {
            return this.Dictionary.Values.GetEnumerator();
        }

        /// <summary>
        /// Returns the CopyDataChannel at the specified 0-based index.
        /// </summary>
        public CopyDataChannel this[int index]
        {
            get
            {
                CopyDataChannel ret = null;
                int i = 0;
                foreach (CopyDataChannel cdc in this.Dictionary.Values)
                {
                    i++;
                    if (i == index)
                    {
                        ret = cdc;
                        break;
                    }
                }
                return ret;
            }
        }
        /// <summary>
        /// Returns the CopyDataChannel for the specified channelName
        /// </summary>
        public CopyDataChannel this[string channelName]
        {
            get
            {
                return (CopyDataChannel)this.Dictionary[channelName];
            }
        }
        /// <summary>
        /// Adds a new channel on which this application can send and
        /// receive messages.
        /// </summary>
        public void Add(string channelName)
        {
            CopyDataChannel cdc = new CopyDataChannel(owner, channelName);
            this.Dictionary.Add(channelName, cdc);
        }
        /// <summary>
        /// Removes an existing channel.
        /// </summary>
        /// <param name="channelName">The channel to remove</param>
        public void Remove(string channelName)
        {
            this.Dictionary.Remove(channelName);
        }
        /// <summary>
        /// Gets/sets whether this channel contains a CopyDataChannel
        /// for the specified channelName.
        /// </summary>
        public bool Contains(string channelName)
        {
            return this.Dictionary.Contains(channelName);
        }

        /// <summary>
        /// Ensures the resources associated with a CopyDataChannel
        /// object collected by this class are cleared up.
        /// </summary>
        protected override void OnClear()
        {
            foreach (CopyDataChannel cdc in this.Dictionary.Values)
            {
                cdc.Dispose();
            }
            base.OnClear();
        }

        /// <summary>
        /// Ensures any resoures associated with the CopyDataChannel object
        /// which has been removed are cleared up.
        /// </summary>
        /// <param name="key">The channelName</param>
        /// <param name="data">The CopyDataChannel object which has
        /// just been removed</param>
        protected override void OnRemoveComplete(Object key, System.Object data)
        {
            ((CopyDataChannel)data).Dispose();
            base.OnRemove(key, data);
        }

        /// <summary>
        /// If the form's handle changes, the properties associated
        /// with the window need to be cleared up. This override ensures
        /// that it is done.  Note that the CopyData class will then
        /// stop responding to events and it should be recreated once
        /// the new handle has been assigned.
        /// </summary>
        public void OnHandleChange()
        {
            foreach (CopyDataChannel cdc in this.Dictionary.Values)
            {
                cdc.OnHandleChange();
            }
        }

        /// <summary>
        /// Constructs a new instance of the CopyDataChannels collection.
        /// Automatically managed by the CopyData class.
        /// </summary>
        /// <param name="owner">The NativeWindow this collection
        /// will be associated with</param>
        internal CopyDataChannels(NativeWindow owner)
        {
            this.owner = owner;
        }
    }

    /// <summary>
    /// A channel on which messages can be sent.
    /// </summary>
    public class CopyDataChannel : IDisposable
    {
        #region Unmanaged Code
        [DllImport("user32", CharSet = CharSet.Auto)]
        private extern static int GetProp(
            IntPtr hwnd,
            string lpString);
        [DllImport("user32", CharSet = CharSet.Auto)]
        private extern static int SetProp(
            IntPtr hwnd,
            string lpString,
            int hData);
        [DllImport("user32", CharSet = CharSet.Auto)]
        private extern static int RemoveProp(
            IntPtr hwnd,
            string lpString);

        [DllImport("user32", CharSet = CharSet.Auto)]
        private extern static int SendMessage(
            IntPtr hwnd,
            int wMsg,
            int wParam,
            ref COPYDATASTRUCT lParam
            );

        [StructLayout(LayoutKind.Sequential)]
        private struct COPYDATASTRUCT
        {
            public IntPtr dwData;
            public int cbData;
            public IntPtr lpData;
        }

        private const int WM_COPYDATA = 0x4A;
        #endregion

        #region Member Variables
        private string channelName = "";
        private bool disposed = false;
        private NativeWindow owner = null;
        private bool recreateChannel = false;
        #endregion

        /// <summary>
        /// Gets the name associated with this channel.
        /// </summary>
        public string ChannelName
        {
            get
            {
                return this.channelName;
            }
        }

        /// <summary>
        /// Sends the specified object on this channel to any other
        /// applications which are listening.  The object must have the
        /// SerializableAttribute set, or must implement ISerializable.
        /// </summary>
        /// <param name="obj">The object to send</param>
        /// <returns>The number of recipients</returns>
        public int Send(object obj)
        {
            int recipients = 0;

            if (disposed)
            {
                throw new InvalidOperationException("Object has been disposed");
            }

            if (recreateChannel) // handle has changed
            {
                addChannel();
            }

            CopyDataObjectData cdo = new CopyDataObjectData(obj, channelName);

            // Try to do a binary serialization on obj.
            // This will throw and exception if the object to
            // be passed isn't serializable.
            BinaryFormatter b = new BinaryFormatter();
            MemoryStream stream = new MemoryStream();
            b.Serialize(stream, cdo);
            stream.Flush();

            // Now move the data into a pointer so we can send
            // it using WM_COPYDATA:
            // Get the length of the data:
            int dataSize = (int)stream.Length;
            if (dataSize > 0)
            {
                // This isn't very efficient if your data is very large.
                // First we copy to a byte array, then copy to a CoTask 
                // Mem object... And when we use WM_COPYDATA windows will
                // make yet another copy!  But if you're talking about 4K
                // or less of data then it doesn't really matter.
                byte[] data = new byte[dataSize];
                stream.Seek(0, SeekOrigin.Begin);
                stream.Read(data, 0, dataSize);
                IntPtr ptrData = Marshal.AllocCoTaskMem(dataSize);
                Marshal.Copy(data, 0, ptrData, dataSize);

                // Enumerate all windows which have the
                // channel name, send the data to each one
                EnumWindows ew = new EnumWindows();
                ew.GetWindows();

                // Send the data to each window identified on
                // the channel:
                foreach (EnumWindowsItem window in ew.Items)
                {
                    if (!window.Handle.Equals(this.owner.Handle))
                    {
                        if (GetProp(window.Handle, this.channelName) != 0)
                        {
                            COPYDATASTRUCT cds = new COPYDATASTRUCT();
                            cds.cbData = dataSize;
                            cds.dwData = IntPtr.Zero;
                            cds.lpData = ptrData;
                            int res = SendMessage(window.Handle, WM_COPYDATA, (int)owner.Handle, ref cds);
                            recipients += (Marshal.GetLastWin32Error() == 0 ? 1 : 0);
                        }
                    }
                }

                // Clear up the data:
                Marshal.FreeCoTaskMem(ptrData);
            }
            stream.Close();

            return recipients;
        }

        private void addChannel()
        {
            // Tag this window with property "channelName"
            SetProp(owner.Handle, this.channelName, (int)owner.Handle);

        }
        private void removeChannel()
        {
            // Remove the "channelName" property from this window
            RemoveProp(owner.Handle, this.channelName);
        }

        /// <summary>
        /// If the form's handle changes, the properties associated
        /// with the window need to be cleared up. This method ensures
        /// that it is done.  Note that the CopyData class will then
        /// stop responding to events and it should be recreated once
        /// the new handle has been assigned.
        /// </summary>
        public void OnHandleChange()
        {
            removeChannel();
            recreateChannel = true;
        }

        /// <summary>
        /// Clears up any resources associated with this channel.
        /// </summary>
        public void Dispose()
        {
            if (!disposed)
            {
                if (channelName.Length > 0)
                {
                    removeChannel();
                }
                channelName = "";
                disposed = true;
                GC.SuppressFinalize(this);
            }
        }

        /// <summary>
        /// Constructs a new instance of a CopyData channel.  Called
        /// automatically by the CopyDataChannels collection.
        /// </summary>
        /// <param name="owner">The owning native window</param>
        /// <param name="channelName">The name of the channel to
        /// send messages on</param>
        internal CopyDataChannel(NativeWindow owner, string channelName)
        {
            this.owner = owner;
            this.channelName = channelName;
            addChannel();
        }

        ~CopyDataChannel()
        {
            Dispose();
        }
    }

    /// <summary>
    /// A class which wraps the data being copied, used
    /// internally within the CopyData class objects.
    /// </summary>
    [Serializable()]
    internal class CopyDataObjectData
    {
        /// <summary>
        /// The Object to copy.  Must be Serializable.
        /// </summary>
        public object Data;
        /// <summary>
        /// The date and time this object was sent.
        /// </summary>
        public DateTime Sent;
        /// <summary>
        /// The name of the channel this object is being sent on
        /// </summary>
        public string Channel;

        /// <summary>
        /// Constructs a new instance of this object
        /// </summary>
        /// <param name="data">The data to copy</param>
        /// <param name="channel">The channel name to send on</param>
        /// <exception cref="ArgumentException">If data is not serializable.</exception>
        public CopyDataObjectData(object data, string channel)
        {
            Data = data;
            if (!data.GetType().IsSerializable)
            {
                throw new ArgumentException("Data object must be serializable.", "data");
            }
            Channel = channel;
            Sent = DateTime.Now;
        }
    }
}
