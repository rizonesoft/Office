using DevExpress.XtraSplashScreen;

namespace Rizonesoft.Office.UI;

/// <summary>
/// Manages overlay screens for the application.
/// </summary>
public class OverlayManager : IDisposable
{
    private IOverlaySplashScreenHandle? _overlaySplashScreenHandle;

    private static readonly OverlayWindowOptions DefaultOptions = new()
    {
        Opacity = 0.6f,
        FadeIn = true,
        FadeOut = true,
        ImageSize = new Size(100, 100),
        AnimationType = WaitAnimationType.Image
        
    };

    /// <summary>
    /// Shows an overlay on the specified control with default options.
    /// </summary>
    /// <param name="ownerControl">The control on which the overlay will be shown.</param>
    public void ShowOverlay(Control ownerControl)
    {
        ShowOverlay(ownerControl, DefaultOptions);
    }

    /// <summary>
    /// Shows an overlay on the specified control with custom options.
    /// </summary>
    /// <param name="ownerControl">The control on which the overlay will be shown.</param>
    /// <param name="options">The overlay window options to use for the overlay.</param>
    public void ShowOverlay(Control ownerControl, OverlayWindowOptions options)
    {
        if (_overlaySplashScreenHandle != null)
            return;

        _overlaySplashScreenHandle = SplashScreenManager.ShowOverlayForm(ownerControl, options);
    }

    /// <summary>
    /// Disposes the overlay screen.
    /// </summary>
    public void DisposeOverlay()
    {
        _overlaySplashScreenHandle?.Dispose();
        _overlaySplashScreenHandle = null;
    }

    /// <summary>
    /// Disposes the resources used by the <see cref="OverlayManager"/>.
    /// </summary>
    void IDisposable.Dispose()
    {
        DisposeOverlay();
    }
}