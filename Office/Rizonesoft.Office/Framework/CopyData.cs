using Newtonsoft.Json;
using System.IO;
using System.Runtime.InteropServices;

namespace Rizonesoft.Office.Framework;

/// <summary>
/// Represents the method that will handle an event when data is received.
/// </summary>
/// <param name="sender">The source of the event.</param>
/// <param name="e">The data received event arguments.</param>
public delegate void DataReceivedEventHandler(object sender, DataReceivedEventArgs e);

/// <summary>
/// Represents the CopyData class which handles copying data and notifying when data is received.
/// </summary>
public sealed class CopyData : NativeWindow, IDisposable
{
    /// <summary>
    /// Event triggered when data is received.
    /// </summary>
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

    /// <summary>
    /// Processes Windows messages.
    /// </summary>
    /// <param name="m">The Windows Message to process.</param>
    protected override void WndProc(ref Message m)
    {
        switch (m.Msg)
        {
            case WmCopydata:
                HandleCopyData(ref m);
                break;
            case WmDestroy:
                HandleDestroy();
                break;
        }

        base.WndProc(ref m);
    }

    private void HandleCopyData(ref Message m)
    {
        var cds = (CopyDataStruct)(Marshal.PtrToStructure(m.LParam, typeof(CopyDataStruct)) ??
                                   throw new InvalidOperationException());
        if (cds.cbData <= 0) return;
        var data = new byte[cds.cbData];
        Marshal.Copy(cds.lpData, data, 0, cds.cbData);
        var stream = new MemoryStream(data);
        var serializer = new JsonSerializer();
        using var reader = new StreamReader(stream);
        using var jsonReader = new JsonTextReader(reader);
        var cdo = serializer.Deserialize<CopyDataObjectData>(jsonReader);
        if (Channels == null || !Channels.Contains(cdo?.Channel)) return;
        if (cdo != null)
        {
            var d = new DataReceivedEventArgs(cdo.Channel, cdo.Data, cdo.Sent);
            OnDataReceived(d);
        }

        m.Result = 1;
    }

    private void HandleDestroy()
    {
        Channels?.OnHandleChange();
        base.OnHandleChange();
    }

    private void OnDataReceived(DataReceivedEventArgs e)
    {
        DataReceived?.Invoke(this, e);
    }

    /// <summary>
    /// Handles the event that occurs when the control's handle changes.
    /// </summary>
    protected override void OnHandleChange()
    {
        base.OnHandleChange();
        Channels?.OnHandleChange();
    }

    /// <summary>
    /// Gets or sets the channels associated with the CopyData instance.
    /// </summary>
    public CopyDataChannels? Channels { get; private set; }

    /// <summary>
    /// Disposes the CopyData object, releasing all allocated resources.
    /// </summary>
    public void Dispose()
    {
        if (disposed) return;
        disposed = true;
        Channels?.Clear();
        Channels = null;
        GC.SuppressFinalize(this);
    }

    /// <summary>
    /// Initializes a new instance of the <see cref="CopyData"/> class.
    /// </summary>
    public CopyData()
    {
        Channels = new CopyDataChannels(this);
    }

    /// <summary>
    /// Destructor for the CopyData class.
    /// </summary>
    ~CopyData()
    {
        Dispose();
    }
}

/// <summary>
/// Represents the arguments for the DataReceived event.
/// </summary>
public sealed class DataReceivedEventArgs
{
    /// <summary>
    /// Gets the name of the channel from which the data was received. Could be null if not provided.
    /// </summary>
    public string? ChannelName { get; }

    /// <summary>
    /// Gets the data that was received. Could be null if no data was sent.
    /// </summary>
    public object? Data { get; }

    /// <summary>
    /// Gets the time when the data was sent.
    /// </summary>
    public DateTime Sent { get; }

    /// <summary>
    /// Gets the time when the data was received.
    /// </summary>
    public DateTime Received { get; }

    /// <summary>
    /// Initializes a new instance of the DataReceivedEventArgs class.
    /// </summary>
    /// <param name="channelName">The name of the channel from which the data was received.</param>
    /// <param name="data">The data that was received.</param>
    /// <param name="sent">The time when the data was sent.</param>
    public DataReceivedEventArgs(string? channelName, object? data, DateTime sent)
    {
        ChannelName = channelName;
        Data = data;
        Sent = sent;
        Received = DateTime.UtcNow;
    }
}

/// <summary>
/// The CopyDataChannels class is a collection of CopyDataChannel objects.
/// It provides methods to add, remove, and check the presence of channels.
/// </summary>
public sealed class CopyDataChannels
{
    private readonly NativeWindow owner;
    private readonly Dictionary<string, CopyDataChannel> Dictionary = new();

    /// <summary>
    /// Retrieves a CopyDataChannel by its index.
    /// </summary>
    public CopyDataChannel? this[int index] => Dictionary.Values.ElementAtOrDefault(index);

    /// <summary>
    /// Retrieves a CopyDataChannel by its channel name.
    /// </summary>
    public CopyDataChannel? this[string channelName] => Dictionary.TryGetValue(channelName, out var channel) ? channel : null;

    /// <summary>
    /// Add a new CopyDataChannel to the collection.
    /// </summary>
    public void Add(string? channelName)
    {
        if (channelName == null) return;

        var cdc = new CopyDataChannel(owner, channelName);
        Dictionary.Add(channelName, cdc);
    }

    /// <summary>
    /// Removes a CopyDataChannel from the collection.
    /// </summary>
    public void Remove(string channelName)
    {
        if (!Dictionary.TryGetValue(channelName, out var channel)) return;
        channel.Dispose();
        Dictionary.Remove(channelName);
    }

    /// <summary>
    /// Checks if a channel exists in the collection.
    /// </summary>
    internal bool Contains(string? channelName) => channelName != null && Dictionary.ContainsKey(channelName);

    /// <summary>
    /// Clears the collection and disposes all channels.
    /// </summary>
    public void Clear() => OnClear();

    /// <summary>
    /// Protected method for clearing the dictionary, could be overridden in the future if needed.
    /// </summary>
    private void OnClear()
    {
        foreach (var cdc in Dictionary.Values)
        {
            cdc.Dispose();
        }
        Dictionary.Clear();
    }

    /// <summary>
    /// Handles change of handles on all channels.
    /// </summary>
    internal void OnHandleChange()
    {
        foreach (var cdc in Dictionary.Values)
        {
            cdc.OnHandleChange();
        }
    }

    /// <summary>
    /// Creates a new instance of CopyDataChannels.
    /// </summary>
    internal CopyDataChannels(NativeWindow owner)
    {
        this.owner = owner;
    }
}

/// <summary>
/// Represents a channel for copying data using the Windows user32 library.
/// </summary>
public sealed partial class CopyDataChannel : IDisposable
{
    // Importing necessary methods from user32.dll
    [LibraryImport("user32", EntryPoint = "GetPropW", StringMarshalling = StringMarshalling.Utf16)]
    private static partial int GetProp(nint hwnd, string? lpString);
    [LibraryImport("user32", EntryPoint = "SetPropW", StringMarshalling = StringMarshalling.Utf16)]
    private static partial void SetProp(IntPtr hwnd, string? lpString, int hData);
    [LibraryImport("user32", EntryPoint = "RemovePropW", StringMarshalling = StringMarshalling.Utf16)]
    private static partial void RemoveProp(IntPtr hwnd, string? lpString);
    [LibraryImport("user32", EntryPoint = "SendMessageW")]
    private static partial int SendMessage(nint hwnd, int wMsg, int wParam, ref CopyDataStruct lParam);

    // Struct representing the data to be copied.
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

    /// <summary>
    /// Gets or sets the name of the channel for copying data.
    /// </summary>
    private string? ChannelName { get; set; }

    /// <summary>
    /// Sends the specified object on the channel.
    /// </summary>
    /// <param name="obj">The object to send.</param>
    /// <returns>The number of recipients that received the object.</returns>
    /// <exception cref="InvalidOperationException">Thrown if the channel has been disposed.</exception>
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

            if (ew.Items != null)
            {
                // ReSharper disable once LoopCanBeConvertedToQuery
                foreach (EnumWindowsItem window in ew.Items)
                {
                    if (window.Handle.Equals(owner.Handle)) continue;
                    if (GetProp(window.Handle, ChannelName) == 0) continue;
                    var cds = new CopyDataStruct
                    {
                        cbData = dataSize,
                        dwData = nint.Zero,
                        lpData = ptrData
                    };
                    // ReSharper disable once UnusedVariable
                    var res = SendMessage(window.Handle, WmCopydata, (int)owner.Handle, ref cds);
                    recipients += Marshal.GetLastWin32Error() == 0 ? 1 : 0;
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

    /// <summary>
    /// Disposes the CopyDataChannel instance, releasing all allocated resources.
    /// </summary>
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
        ChannelName = channelName;
        AddChannel();
    }

    /// <summary>
    /// Disposes the channel, removing it if necessary.
    /// </summary>
    ~CopyDataChannel()
    {
        Dispose();
    }
}

/// <summary>
/// Represents a serializable object that is intended to be copied and sent over a specified channel.
/// </summary>
[Serializable]
internal class CopyDataObjectData
{
    /// <summary>
    /// Gets or sets the serializable data to be copied.
    /// </summary>
    /// <exception cref="ArgumentException">Thrown when trying to set non-serializable data.</exception>
    public object? Data
    {
        get => _data;
        set
        {
            if (value != null && !value.GetType().IsSerializable)
            {
                throw new ArgumentException(@"Honey, you can't serialize this object! Try something else.", nameof(value));
            }

            _data = value;
        }
    }
    private object? _data;

    /// <summary>
    /// Gets the date and time this object was sent.
    /// </summary>
    public DateTime Sent { get; }

    /// <summary>
    /// Gets or sets the name of the channel this object is being sent on.
    /// </summary>
    public string? Channel { get; set; }

    /// <summary>
    /// Constructs a new instance of this object with the specified data and channel.
    /// </summary>
    /// <param name="data">The data to copy.</param>
    /// <param name="channel">The channel name to send on.</param>
    public CopyDataObjectData(object? data, string? channel)
    {
        Data = data;
        Channel = channel;
        Sent = DateTime.Now;
    }
}