using DevExpress.XtraBars;
using Rizonesoft.Office.Localization;

namespace Rizonesoft.Office.UI.Ribbon.Buttons;

/// <summary>
/// Represents the base class for Ribbon button items.
/// </summary>
public abstract class ButtonItemBase : IDisposable
{
    /// <summary>
    /// The BarButtonItem associated with the derived ButtonItemBase class.
    /// </summary>
    protected readonly BarButtonItem _barButtonItem;
    private bool _disposed;

    /// <summary>
    /// Initializes a new instance of the ButtonItemBase class with the specified BarButtonItem.
    /// </summary>
    /// <param name="barButtonItem">The BarButtonItem to be configured.</param>
    protected ButtonItemBase(BarButtonItem barButtonItem)
    {
        _barButtonItem = barButtonItem ?? throw new ArgumentNullException(nameof(barButtonItem));
        LanguageManager.LanguageChanged += OnLanguageChanged;
    }

    /// <summary>
    /// Initializes the BarButtonItem with required properties and event handlers.
    /// </summary>
    protected abstract void InitializeBarButtonItem();

    /// <summary>
    /// The method that gets called when the button is clicked.
    /// </summary>
    protected abstract void OnButtonClick();

    /// <summary>
    /// Updates the language of the BarButtonItem.
    /// </summary>
    protected abstract void UpdateLanguage();

    /// <summary>
    /// Handles the LanguageChanged event and updates the language of the associated BarButtonItem.
    /// </summary>
    /// <param name="sender">The source of the event.</param>
    /// <param name="e">The <see cref="EventArgs"/> instance containing the event data.</param>
    private void OnLanguageChanged(object? sender, EventArgs e)
    {
        UpdateLanguage();
    }


    /// <summary>
    /// Creates a new instance of the specified derived class.
    /// </summary>
    /// <typeparam name="T">The type of the derived class.</typeparam>
    /// <param name="barButtonItem">The BarButtonItem to be configured.</param>
    /// <returns>A new instance of the specified derived class.</returns>
    public static T Create<T>(BarButtonItem barButtonItem) where T : ButtonItemBase
    {
        var instance = (T)Activator.CreateInstance(typeof(T), barButtonItem)!;
        instance.InitializeBarButtonItem();
        return instance;
    }

    /// <summary>
    /// Disposes the current instance of ButtonItemBase and releases resources.
    /// </summary>
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    /// <summary>
    /// Disposes the current instance of ButtonItemBase and releases resources.
    /// </summary>
    /// <param name="disposing">True to release both managed and unmanaged resources; False to release only unmanaged resources.</param>
    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;
        if (disposing)
        {
            LanguageManager.LanguageChanged -= OnLanguageChanged;
        }

        _disposed = true;
    }
}