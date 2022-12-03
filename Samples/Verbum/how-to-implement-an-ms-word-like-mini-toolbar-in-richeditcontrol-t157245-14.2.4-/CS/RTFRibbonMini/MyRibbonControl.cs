// Developer Express Code Central Example:
// How to implement an MS Word-like Mini Toolbar in RichEditControl
// 
// This example demonstrates how to implement the MS Word-like Mini Toolbar feature
// using a RibbonMiniToolbar
// (https://documentation.devexpress.com/#WindowsForms/clsDevExpressXtraBarsRibbonRibbonMiniToolbartopic)
// component. It is a popup toolbar, whose transparency depends on the distance
// from the mouse cursor. Show this toolbar for the selected text in the
// RichEditControl document separately and display it together with a regular
// context menu in the RichEditControl.PopupMenuShowing event handler.
// 
// You can find sample updates and versions for different programming languages here:
// http://www.devexpress.com/example=T157245

using System;
using System.Collections.Generic;
using System.Linq;
using DevExpress.XtraBars;
using DevExpress.XtraBars.Controls;
using DevExpress.XtraBars.Ribbon;
using DevExpress.XtraBars.ViewInfo;

namespace RTFRibbonMini {
    public class MyRibbonControl : RibbonControl {

        public MyRibbonControl() {
        }
        protected override RibbonBarManager CreateBarManager() {
            return new MyRibbonBarManager(this);
        }
    }



    public class MyRibbonBarManager : RibbonBarManager {
        public MyRibbonBarManager(RibbonControl ribbonControl)
            : base(ribbonControl) {

        }
        protected override BarSelectionInfo CreateSelectionInfo() {
            return new AdvancedBarSelectionInfo(this);
        }
    }



    public class AdvancedBarSelectionInfo : RibbonSelectionInfo {
        public AdvancedBarSelectionInfo(RibbonBarManager manager)
            : base(manager) {
        }
        protected override void CheckAndClosePopups(BarItemLink newLink) {
            BarPopupCollection popups = OpenedPopups;
            PopupMenuBarControl miniToolBar = popups.OfType<PopupMenuBarControl>().FirstOrDefault();
            if(miniToolBar != null)
                return;

            base.CheckAndClosePopups(newLink);
        }

        protected override void PressLinkCore(BarItemLink link, bool isArrow) {
            for(int n = OpenedPopups.Count - 1; n >= 0; n--) {
                IPopup popup = OpenedPopups[n] as IPopup;
                if(popup.ContainsLink(link)) {

                    for(int i = 0; i < Manager.Ribbon.MiniToolbars.Count; i++) {
                        Manager.Ribbon.MiniToolbars[i].Hide();
                    }
                }
            }
            base.PressLinkCore(link, isArrow);
        }
    }
}
