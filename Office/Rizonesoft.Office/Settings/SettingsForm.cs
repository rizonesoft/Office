using DevExpress.XtraEditors.Controls;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Localization;
using Rizonesoft.Office.UI.Forms;
using Rizonesoft.Office.Utilities;
using System.Globalization;

namespace Rizonesoft.Office.Settings;

/// <summary>
/// The SettingsForm class represents the form for managing Rizonesoft Office settings.
/// </summary>
public partial class SettingsForm : FormBase
{

    /// <summary>
    /// Initializes a new instance of the SettingsForm class.
    /// </summary>
    public SettingsForm()
    {
        InitializeComponent();
        Load += async (_, _) => await SettingsForm_LoadAsync().ConfigureAwait(false);
        SpinLoggingFileLimit.Properties.IsFloatValue = false;
        InitializeLanguageList();
        LanguageManager.LanguageChanged += LanguageManager_LanguageChanged;
        UpdateLanguage();
    }

    /// <summary>
    /// Initializes the language list for the application.
    /// </summary>
    private void InitializeLanguageList()
    {
        languageList.Items.Clear();
        foreach (var language in LanguageManager.availableLanguages)
        {
            var item = new ImageListBoxItem()
            {
                Value = language.CultureInfo?.NativeName,
                ImageOptions = { SvgImage = language.FlagImage, SvgImageSize = new Size(30, 30) }
            };

            languageList.Items.Add(item);

            if ((string)item.Value! == Thread.CurrentThread.CurrentCulture.NativeName)
            {
                languageList.SelectedItem = item;
            }
        }

        languageList.SelectedValueChanged += LanguageList_SelectedValueChangedAsync;
    }

    /// <summary>
    /// Handles language list value changed event.
    /// </summary>
    private async void LanguageList_SelectedValueChangedAsync(object? sender, EventArgs e)
    {
        var allCultures = CultureInfo.GetCultures(CultureTypes.AllCultures);
        var selectedLanguage = languageList.SelectedValue.ToString();
        var selectedCulture = allCultures.FirstOrDefault(c => c.NativeName == selectedLanguage);

        if (selectedCulture == null) return;
        LanguageManager.SetCultureInfo(selectedCulture.Name);
        GlobalSettings.LanguageCode = LanguageManager.LanguageCode;
    }

    /// <summary>
    /// Loads the settings for the form asynchronously.
    /// </summary>
    private async Task SettingsForm_LoadAsync()
    {
        // Always directly read from the registry
        radGroupInterval.SelectedIndex = RollingIntervalToRadioIndex(GlobalSettings.LogRollingInterval);
        SpinLoggingFileLimit.Value = GlobalSettings.LogFileLimit;
    }

    /// <summary>
    /// Saves the settings for the form asynchronously.
    /// </summary>
    private async Task SaveSettingsAsync()
    {
        // Update the properties directly. This will save the changes to the registry.
        GlobalSettings.LogRollingInterval = RadioIndexToRollingInterval(radGroupInterval.SelectedIndex);
        GlobalSettings.LogFileLimit = Convert.ToInt32(SpinLoggingFileLimit.Value);
    }

    /// <summary>
    /// Updates the language for the form.
    /// </summary>
    private void UpdateLanguage()
    {
        Text = Strings.SettingsForm_Title;
        tabNavGeneral.Caption = Strings.SettingsForm_TabNavPage_General;
        tabNavAdvanced.Caption = Strings.SettingsForm_TabNavPage_Advanced;
        accElementLogging.Text = Strings.SettingsForm_Accordion_Logging;
        accElementLanguage.Text = Strings.SettingsForm_Accordion_Localization;
        lblLocalDescription.Text = Strings.SettingsForm_lblLocalDescription;
        lblSelectLanguage.Text = Strings.SettingsForm_lblSelectLanguage;
        lblCurrLangLabel.Text = Strings.SettingsForm_lblCurrLangLabel;
        lblCurrCultLabel.Text = Strings.SettingsForm_lblCurrCultLabel;
        groupRollingInterval.Text = Strings.SettingsForm_Group_Rolling_Interval;
        radGroupInterval.ToolTipTitle = Strings.SettingsForm_Group_RollingInterval_ToolTipTitle;
        radGroupInterval.ToolTip = Strings.SettingsForm_Group_RollingInterval_ToolTip;
        lblLoggingFileLimit.Text = Strings.SettingsForm_Label_File_Limit;
        BtnOpenLog.Text = Strings.SettingsForm_Button_OpenLog;
        BtnOpenLog.ToolTipTitle = Strings.SettingsForm_Button_OpenLog_ToolTipTitle;
        BtnOpenLog.ToolTip = Strings.SettingsForm_Button_OpenLog_ToolTip;
        BtnCleanLog.Text = Strings.SettingsForm_Button_CleanLog;
        BtnCleanLog.ToolTipTitle = Strings.SettingsForm_Button_CleanLog_TootlTipTitle;
        BtnCleanLog.ToolTip = Strings.SettingsForm_Button_CleanLog_TootlTip;
        radGroupInterval.Properties.Items[0].Description = Strings.SettingsForm_LogInterval_Minute;
        radGroupInterval.Properties.Items[1].Description = Strings.SettingsForm_LogInterval_Hour;
        radGroupInterval.Properties.Items[2].Description = Strings.SettingsForm_LogInterval_Day;
        radGroupInterval.Properties.Items[3].Description = Strings.SettingsForm_LogInterval_Month;
        radGroupInterval.Properties.Items[4].Description = Strings.SettingsForm_LogInterval_Infinite;
        SpinLoggingFileLimit.ToolTipTitle = Strings.SettingsForm_LogFileLimit_ToolTipTitle;
        SpinLoggingFileLimit.ToolTip = Strings.SettingsForm_LogFileLimit_ToolTip;

        lblCurrLang.Text = $@"{CultureInfo.CurrentCulture.NativeName} ({CultureInfo.CurrentCulture.Name})";
        lblCurrCult.Text = CultureInfo.CurrentCulture.ThreeLetterISOLanguageName;

    }

    /// <summary>
    /// Handles language changed event.
    /// </summary>
    private void LanguageManager_LanguageChanged(object? sender, EventArgs e)
    {
        UpdateLanguage();
    }

    /// <summary>
    /// Handles radio group interval selection change.
    /// </summary>
    private void RadGroupInterval_SelectedIndexChanged(object sender, EventArgs e)
    {
        GlobalSettings.LogRollingInterval = RadioIndexToRollingInterval(radGroupInterval.SelectedIndex);
    }

    /// <summary>
    /// Handles form closing event.
    /// </summary>
    private async void SettingsForm_FormClosingAsync(object sender, FormClosingEventArgs e)
    {
        await SaveSettingsAsync().ConfigureAwait(false);
    }

    /// <summary>
    /// Converts radio index to rolling interval.
    /// </summary>
    private static int RadioIndexToRollingInterval(int radioIndex)
    {
        return 5 - radioIndex;
    }

    /// <summary>
    /// Converts rolling interval to radio index.
    /// </summary>
    private static int RollingIntervalToRadioIndex(int rollingInterval)
    {
        return 5 - rollingInterval;
    }

    /// <summary>
    /// Handles the value changed event for the logging file limit.
    /// </summary>
    private void SpinLoggingFileLimit_ValueChanged(object sender, EventArgs e)
    {
        // Update the LogFileLimit property directly. This will save the changes to the registry.
        GlobalSettings.LogFileLimit = Convert.ToInt32(SpinLoggingFileLimit.Value);
    }

    /// <summary>
    /// Handles the click event for the open log button.
    /// </summary>
    private void BtnOpenLog_Click(object sender, EventArgs e)
    {
        LogFileManager.OpenLogDirectory();
    }

    /// <summary>
    /// Handles the click event for the clean log button.
    /// </summary>
    private void BtnCleanLog_Click(object sender, EventArgs e)
    {
        LogFileManager.CleanLogDirectory();
    }
}
