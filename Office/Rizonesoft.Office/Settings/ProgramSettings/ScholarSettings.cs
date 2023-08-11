using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Rizonesoft.Office.Settings.ProgramSettings;

/// <summary>
/// Class that holds the application-wide settings of Rizonesoft Office.
/// </summary>
public static class ScholarSettings
{
    private const int DefaultNavigationPaneWidth = 400;
    private const string NavigationPaneWidthRegistryKey = "NavigationPaneWidth";

    private static readonly RegistrySetting<int> navigationPaneWidth = new(NavigationPaneWidthRegistryKey, DefaultNavigationPaneWidth, RegistryOperations.SettingScope.Local);

    public static int NavigationPaneWidth
    {
        get => navigationPaneWidth.Value;
        set => navigationPaneWidth.Value = value;
    }
}
