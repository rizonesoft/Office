using DevExpress.Utils;
using DevExpress.XtraBars;
using DevExpress.XtraEditors;
using Rizonesoft.Office.ErrorHandling;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Settings;
using Rizonesoft.Office.Toast;
using Rizonesoft.Office.Utilities;
using System.Globalization;

namespace Rizonesoft.Office.Localization;

/// <summary>
/// A class responsible for managing the application's language and culture settings.
/// </summary>
public class LanguageManager
{
    /// <summary>
    /// A class responsible for managing the application's language and culture settings.
    /// </summary>
    public static event EventHandler? LanguageChanged;

    /// <summary>
    /// Gets or sets the language code for the application.
    /// </summary>
    public static string LanguageCode { get; set; } = "en";

    /// <summary>
    /// A list of available languages and their corresponding flag image resources.
    /// </summary>
    public static readonly List<Language> availableLanguages = new()
    {
        // Add languages and their corresponding flag image resource names here
        new Language(new CultureInfo("af"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.af.svg")),
        new Language(new CultureInfo("cs"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.cs.svg")),
        new Language(new CultureInfo("de"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.de.svg")),
        new Language(new CultureInfo("en"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.en.svg")),
        new Language(new CultureInfo("es"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.es.svg")),
        new Language(new CultureInfo("fr"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.fr.svg")),
        new Language(new CultureInfo("it"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.it.svg")),
        new Language(new CultureInfo("ja"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.ja.svg")),
        new Language(new CultureInfo("ko"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.ko.svg")),
        new Language(new CultureInfo("pl"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.pl.svg")),
        new Language(new CultureInfo("pt-BR"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.pt-BR.svg")),
        new Language(new CultureInfo("ru"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.ru.svg")),
        new Language(new CultureInfo("tr"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.tr.svg")),
        new Language(new CultureInfo("zh-Hans"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.zh-Hans.svg")),
        new Language(new CultureInfo("zh-Hant"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.zh-Hant.svg")),
        new Language(new CultureInfo("zu-ZA"),
            ImageResourceLoader.LoadSvgImageFromResource("Rizonesoft.Office.Localization.Resources.zu-ZA.svg"))
    };

    /// <summary>
    /// Initializes the language menu for the application.
    /// </summary>
    /// <param name="languageDropDownButton">The button that displays the currently selected language.</param>
    /// <param name="languagePopup">The popup menu containing the list of available languages.</param>
    public static void InitializeLanguageMenu(BarItem languageDropDownButton, BarLinksHolder languagePopup)
    {
        try
        {
            LoadLanguages(languageDropDownButton, languagePopup);
        }
        catch (Exception ex)
        {
            Serilogger.LogMessage(LogLevel.Error, "An error occurred while creating the language Drop Down menu.", ex);
            XtraMessageBox.Show(Strings.Language_DropDown_Error, Strings.MessageBox_Error_Title, MessageBoxButtons.OK,
                MessageBoxIcon.Error);
        }
    }

    /// <summary>
    /// Loads the available languages into the language menu.
    /// </summary>
    /// <param name="languageDropDownButton">The button that displays the currently selected language.</param>
    /// <param name="languagePopup">The popup menu containing the list of available languages.</param>
    private static void LoadLanguages(BarItem languageDropDownButton, BarLinksHolder languagePopup)
    {
        try
        {
            // Populate the drop-down button with the available languages and their flag images
            PopulateLanguageMenu(availableLanguages, languageDropDownButton, languagePopup);
            // Set the default language based on the current culture
            SetDefaultLanguage(languageDropDownButton, availableLanguages);
        }
        catch (Exception ex)
        {
            Serilogger.LogMessage(LogLevel.Error, "An error occurred while loading language data.", ex);
            XtraMessageBox.Show(Strings.LoadLanguages_Error, Strings.MessageBox_Error_Title, MessageBoxButtons.OK,
                MessageBoxIcon.Error);
        }
    }

    /// <summary>
    /// Populates the language menu with the available languages and their flag images.
    /// </summary>
    /// <param name="_availableLanguages">The list of available languages.</param>
    /// <param name="languageDropDownButton">The button that displays the currently selected language.</param>
    /// <param name="languagePopup">The popup menu containing the list of available languages.</param>
    private static void PopulateLanguageMenu(List<Language> _availableLanguages,
        BarItem languageDropDownButton, BarLinksHolder languagePopup)
    {
        foreach (var language in _availableLanguages)
        {
            var item = new BarButtonItem
            {
                Caption = language.CultureInfo?.NativeName,
                Tag = language.CultureInfo?.Name,
            };
            item.ImageOptions.SvgImage = language.FlagImage;
            item.ImageOptions.SvgImageColorizationMode = SvgImageColorizationMode.None;
            item.ItemClick += (_, e) => LanguageDropDownButton_ItemClick(e, languageDropDownButton);

            languagePopup.AddItem(item);
        }
    }

    /// <summary>
    /// Sets the default language based on the current culture.
    /// </summary>
    /// <param name="languageDropDownButton">The button that displays the currently selected language.</param>
    /// <param name="_availableLanguages">The list of available languages.</param>
    private static void SetDefaultLanguage(BarItem languageDropDownButton, IEnumerable<Language> _availableLanguages)
    {
        languageDropDownButton.Tag = Thread.CurrentThread.CurrentCulture.Name;
        languageDropDownButton.Caption = Thread.CurrentThread.CurrentCulture.NativeName;
        languageDropDownButton.ImageOptions.SvgImage = _availableLanguages
            .FirstOrDefault(lang => lang.CultureInfo?.Name == Thread.CurrentThread.CurrentCulture.Name)?.FlagImage;
    }

    /// <summary>
    /// Sets the application culture for globalization and localization.
    /// </summary>
    /// <param name="cultureName">The culture name in the format "en-US".</param>
    public static void SetCultureInfo(string cultureName)
    {
        try
        {
            var cultureInfo = new CultureInfo(cultureName);
            Thread.CurrentThread.CurrentCulture = cultureInfo;
            Thread.CurrentThread.CurrentUICulture = cultureInfo;
            LanguageCode = cultureName;

            // Raise the LanguageChanged event
            LanguageChanged?.Invoke(null, EventArgs.Empty);
        }
        catch (CultureNotFoundException ce)
        {
            Serilogger.LogMessage(LogLevel.Error, "An error occurred while saving language data.", ce, cultureName);
            ToastHelper.CreateErrorToast(Strings.Language_CultureInfo_ErrorCaption, Strings.Language_CultureInfo_Error);

            var defaultCulture = new CultureInfo("en-US");
            Thread.CurrentThread.CurrentCulture = defaultCulture;
            Thread.CurrentThread.CurrentUICulture = defaultCulture;
        }
    }

    /// <summary>
    /// Handles the language dropdown button item click event.
    /// </summary>
    /// <param name="e">The event arguments.</param>
    /// <param name="languageDropDownButton">The button that displays the currently selected language.</param>
    private static async void LanguageDropDownButton_ItemClick(ItemClickEventArgs e,
        BarItem languageDropDownButton)
    {
        if (e.Item is not { Tag: string languageCode }) return;
        // Set the new language
        languageDropDownButton.Tag = languageCode;
        languageDropDownButton.Caption = e.Item.Caption;
        languageDropDownButton.ImageOptions.SvgImage = e.Item.ImageOptions.SvgImage;
        SetCultureInfo(languageCode);
        await Task.Run(() => GlobalSettings.LanguageCode = languageCode);
    }

    /// <summary>
    /// Updates the language drop-down button with the provided culture information.
    /// </summary>
    /// <param name="languageDropDownButton">The BarButtonItem representing the language drop-down button.</param>
    /// <param name="newCulture">The CultureInfo object containing the new culture information.</param>
    public static void UpdateLanguageDropDownButton(BarButtonItem languageDropDownButton, CultureInfo newCulture)
    {
        // Find the corresponding language item in the language popup menu
        var matchingItem = languageDropDownButton.Manager.Items.FirstOrDefault(item => item.Tag is string languageCode && languageCode == newCulture.Name);

        if (matchingItem == null) return;
        languageDropDownButton.Tag = newCulture.Name;
        languageDropDownButton.Caption = matchingItem.Caption;
        languageDropDownButton.ImageOptions.SvgImage = matchingItem.ImageOptions.SvgImage;
    }

    /// <summary>
    /// Retrieves the saved language code from the settings.
    /// </summary>
    /// <returns>A task that represents the asynchronous operation. The value of the TResult parameter contains the saved language code.</returns>
    public static Task<string> GetLanguageCodeAsync()
    {
        var languageCode = GlobalSettings.LanguageCode;

        // Check if the retrieved languageCode is null or empty, and if so, return a default language code
        if (string.IsNullOrEmpty(languageCode))
        {
            languageCode = "en";
        }

        return Task.FromResult(languageCode);
    }

}