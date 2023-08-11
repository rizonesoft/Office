using DevExpress.Utils;
using DevExpress.Utils.Svg;
using DevExpress.XtraBars;
using DevExpress.XtraBars.Navigation;
using Rizonesoft.Office.Language;

namespace Rizonesoft.Office.UI;

/// <summary>
/// Contains methods to manage and update SuperToolTip components.
/// </summary>
public static class SuperTipHelper
{
    /// <summary>
    /// Creates a SuperToolTip with the given parameters for the specified BarItem.
    /// </summary>
    /// <param name="barButtonItem">The BarItem for which to create the SuperToolTip.</param>
    /// <param name="tipItemText">The text to display in the SuperToolTip.</param>
    /// <param name="tipFooterUrl">The URL to display in the footer of the SuperToolTip (optional).</param>
    public static void CreateSuperTooltip(BarItem barButtonItem, string tipItemText, string tipFooterUrl = "https://www.rizonesoft.com")
    {
        var superTip = new SuperToolTip();
        var tipItem = new ToolTipItem();
        if (barButtonItem.ImageOptions.SvgImage != null)
        {
            tipItem.ImageOptions.SvgImage = barButtonItem.ImageOptions.SvgImage;
            tipItem.ImageOptions.SvgImageSize = new Size(32, 32);
        }
            
        tipItem.Text = tipItemText;
        var tipFooter = new ToolTipItem();
        superTip.AllowHtmlText = DefaultBoolean.True;
        tipFooter.Text = string.Format(Strings.RibbonButtonSuperTip_LearnMore, tipFooterUrl);
        superTip.Items.AddTitle(barButtonItem.Caption);
        superTip.Items.Add(tipItem);
        superTip.Items.AddSeparator();
        superTip.Items.Add(tipFooter);
        barButtonItem.SuperTip = superTip;
    }

    /// <summary>
    /// Updates the title and text of a SuperToolTip.
    /// </summary>
    /// <param name="superTip">The SuperToolTip to update.</param>
    /// <param name="newTitle">The new title for the SuperToolTip.</param>
    /// <param name="newText">The new text for the SuperToolTip.</param>
    /// <exception cref="InvalidOperationException">Thrown if the SuperToolTip has an unexpected structure.</exception>
    public static void UpdateSuperTip(SuperToolTip superTip, string newTitle, string newText)
    {
        if (superTip == null)
        {
            throw new ArgumentNullException(nameof(superTip));
        }

        if (superTip.Items.Count < 2)
        {
            throw new InvalidOperationException("SuperToolTip has an unexpected structure.");
        }

        SetToolTipItemText<ToolTipTitleItem>(superTip.Items[0], newTitle);
        SetToolTipItemText<ToolTipItem>(superTip.Items[1], newText);
    }

    private static void SetToolTipItemText<T>(BaseToolTipItem item, string newText) where T : BaseToolTipItem
    {
        if (item is T typedItem)
        {
            var textProperty = typeof(T).GetProperty("Text");
            if (textProperty == null) return;
            textProperty.SetValue(typedItem, newText);
        }
        else
        {
            throw new InvalidOperationException($"Item is not of the expected type: {typeof(T)}.");
        }
    }

    /// <summary>
    /// Updates the title, text, and footer of a SuperToolTip for the specified BarButtonItem. Creates a new SuperToolTip if not already set.
    /// </summary>
    /// <param name="barButtonItem">The BarButtonItem whose SuperToolTip to update.</param>
    /// <param name="newText">The new text for the SuperToolTip.</param>
    /// <param name="newFooterUrl">The new footer URL for the SuperToolTip.</param>
    public static void UpdateSuperTipTextAndFooter(BarButtonItem barButtonItem, string newText, string newFooterUrl)
    {
        if (barButtonItem == null)
        {
            throw new ArgumentNullException(nameof(barButtonItem));
        }

        var superTip = barButtonItem.SuperTip;

        if (superTip == null)
        {
            CreateSuperTooltip(barButtonItem, newText, newFooterUrl);
            return;
        }

        if (superTip.Items.Count < 4)
        {
            throw new InvalidOperationException("SuperToolTip has an unexpected structure.");
        }

        if (superTip.Items[0] is ToolTipTitleItem tooltipTitle)
        {
            tooltipTitle.Text = barButtonItem.Caption;
        }
        else
        {
            throw new InvalidOperationException("Item is not of the expected type: ToolTipTitleItem.");
        }

        if (superTip.Items[1] is ToolTipItem tooltipItem)
        {
            tooltipItem.Text = newText;
        }
        else
        {
            throw new InvalidOperationException("Item is not of the expected type: ToolTipItem.");
        }

        if (superTip.Items[3] is ToolTipItem tooltipFooter)
        {
            tooltipFooter.Text = string.Format(Strings.RibbonButtonSuperTip_LearnMore, newFooterUrl);
        }
        else
        {
            throw new InvalidOperationException("Item is not of the expected type: ToolTipItem.");
        }
    }

    /// <summary>
    /// Sets up SuperTip SVG icons for the provided items.
    /// </summary>
    /// <param name="items">An array of bar buttons and navigation pages to set up SuperTip SVG icons for.</param>
    public static void SetupSuperTipSvgIconsForItems(params object[] items)
    {
        foreach (var item in items)
        {
            switch (item)
            {
                case BarButtonItem barButtonItem:
                    SetSuperTipSvgIcon(barButtonItem,
                        btn => btn.SuperTip, btn => btn.ImageOptions.SvgImage);
                    break;
                case TabNavigationPage navPage:
                    SetSuperTipSvgIcon(navPage,
                        page => page.SuperTip, page => page.ImageOptions.SvgImage);
                    break;
            }
        }
    }

    /// <summary>
    /// Sets the SuperTip SVG icon for the specified component.
    /// </summary>
    /// <typeparam name="T">The type of the component.</typeparam>
    /// <param name="component">The component for which to set the SuperTip SVG icon.</param>
    /// <param name="getSuperTip">A function to get the SuperTip from the component.</param>
    /// <param name="getImage">A function to get the SvgImage from the component.</param>
    private static void SetSuperTipSvgIcon<T>(T component, Func<T, SuperToolTip> getSuperTip, Func<T, SvgImage> getImage)
    {
        var superTip = getSuperTip(component);
        var svgImage = getImage(component);

        if (superTip.Items.Count < 2 || superTip.Items[1] is not ToolTipItem tooltipItem)
        {
            return;
        }

        tooltipItem.ImageOptions.SvgImage = svgImage;
    }

}