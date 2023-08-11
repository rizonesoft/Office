using DevExpress.XtraSplashScreen;
using Rizonesoft.Office.Ecosystem;
using Rizonesoft.Office.Framework;
using Rizonesoft.Office.Language;
using Rizonesoft.Office.Programs;
using Rizonesoft.Office.Utilities;

namespace Rizonesoft.Office.UI;

/// <summary>
/// Provides helper methods to manage the splash screen.
/// </summary>
public class SplashScreenHelper
{
    private static readonly string? ProgramName = ProgramConfiguration.ProgramName;

    /// <summary>
    /// Shows the splash screen with the specified parent form.
    /// </summary>
    /// <param name="parentForm">The parent form of the splash screen.</param>
    public static void ShowSplashScreen(Form parentForm)
    {
        var progVersionFull = ProgramConfiguration.Version?.fullVersion;
        var progVersionMajor = ProgramConfiguration.Version?.major;
        var officeVersion = GlobalConfiguration.ProductVersion;

        var fluentSplashOptions = new FluentSplashScreenOptions
        {
            Title = $"{ProgramName} {progVersionMajor}",
            Subtitle = "",
            RightFooter = Strings.SplashScreen_FooterRight,
            LeftFooter = $"{ProgramName} ver. ({progVersionFull})" +
                         $"\nRizonesoft Office ver. ({officeVersion})" +
                         $"\nRuntime {RuntimeHelper.RuntimeVersion}" +
                         $"\n\nCopyright © 2019 - 2023 Rizonetech (Pty) Ltd.\nAll Rights reserved.",
            LoadingIndicatorType = FluentLoadingIndicatorType.Dots,
            Opacity = (int)0.6F,
            AppearanceTitle = { Font = new Font("Segoe UI", 19, FontStyle.Bold) },
            AppearanceSubtitle = { Font = new Font("Segoe UI", 9, FontStyle.Regular) },
            AppearanceRightFooter = { Font = new Font("Segoe UI", 10, FontStyle.Regular) },
            AppearanceLeftFooter = { Font = new Font("Segoe UI", 9, FontStyle.Regular) },
            LogoImageOptions =
            {
                SvgImage = ImageResourceLoader.LoadSvgImageFromResource($"Rizonesoft.Office.Programs.Resources.{ProgramName}.svg"),
                SvgImageSize = new Size(80, 80)
            }
        };

        SplashScreenManager.ShowFluentSplashScreen(
            fluentSplashOptions,
            parentForm: parentForm,
            useFadeIn: true,
            useFadeOut: true,
            throwExceptionIfAlreadyOpened: true,
            startPos: SplashFormStartPosition.CenterScreen

        );
    }

    /// <summary>
    /// Closes the splash screen.
    /// </summary>
    public static void CloseSplashScreen()
    {
        var fluentSplashOptions = new FluentSplashScreenOptions { RightFooter = "Done" };
        SplashScreenManager.Default.SendCommand(FluentSplashScreenCommand.UpdateOptions, fluentSplashOptions);

        SplashScreenManager.CloseForm();
    }
}