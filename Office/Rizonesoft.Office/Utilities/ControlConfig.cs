using DevExpress.Utils;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraTab;
using DevExpress.XtraTabbedMdi;

namespace Rizonesoft.Office.Utilities;

/// <summary>
/// Handles the default configurations for DevExpress controls.
/// Because who has time to set these up every single time, right?
/// </summary>
public static class ControlConfig
{
    /// <summary>
    /// Sets up a bunch of default configurations for XtraTabbedMdiManager.
    /// It's like making your bed in the morning. But for controls.
    /// </summary>
    /// <param name="mdiManager">The XtraTabbedMdiManager instance we're going to configure. Cannot be null because, well, magic isn't real.</param>
    /// <param name="ownerControl">The parent form for the MdiManager. Like its guardian, if you will.</param>
    /// <exception cref="ArgumentNullException">Thrown when the mdiManager is null. Because you can't dress up something that doesn't exist.</exception>
    public static void SetDefaultMdiManagerConfig(XtraTabbedMdiManager mdiManager, RibbonForm ownerControl)
    {
        if (mdiManager == null)
        {
            throw new ArgumentNullException(nameof(mdiManager), 
                @"Sorry to break it to you, but you're trying to configure a ghost object. It's null.");
        }

        mdiManager.AllowDragDrop = DefaultBoolean.True;
        mdiManager.ClosePageButtonShowMode = ClosePageButtonShowMode.InActiveTabPageAndTabControlHeader;
        mdiManager.CloseTabOnMiddleClick = CloseTabOnMiddleClick.Never;
        mdiManager.FloatOnDoubleClick = DefaultBoolean.True;
        mdiManager.FloatOnDrag = DefaultBoolean.True;
        mdiManager.FloatPageDragMode = FloatPageDragMode.Preview;
        mdiManager.HeaderButtons = TabButtons.Prev | TabButtons.Next | TabButtons.Close | TabButtons.Default;
        mdiManager.HeaderButtonsShowMode = TabButtonShowMode.WhenNeeded;
        mdiManager.MdiParent = ownerControl ?? throw new ArgumentNullException(nameof(ownerControl), 
            @"Seems like you forgot to pass in the owner control. We can't leave our MdiManager orphaned, can we?");
        mdiManager.PinPageButtonShowMode = PinPageButtonShowMode.InActiveTabPageHeader;
        mdiManager.SetNextMdiChildMode = SetNextMdiChildMode.Windows;
        mdiManager.ShowFloatingDropHint = DefaultBoolean.True;
        mdiManager.ShowHeaderFocus = DefaultBoolean.True;
        mdiManager.ShowToolTips = DefaultBoolean.True;
        mdiManager.UseDocumentSelector = DefaultBoolean.True;
        mdiManager.UseFormIconAsPageImage = DefaultBoolean.True;
    }
}