' Developer Express Code Central Example:
' How to implement an MS Word-like Mini Toolbar in RichEditControl
' 
' This example demonstrates how to implement the MS Word-like Mini Toolbar feature
' using a RibbonMiniToolbar
' (https://documentation.devexpress.com/#WindowsForms/clsDevExpressXtraBarsRibbonRibbonMiniToolbartopic)
' component. It is a popup toolbar, whose transparency depends on the distance
' from the mouse cursor. Show this toolbar for the selected text in the
' RichEditControl document separately and display it together with a regular
' context menu in the RichEditControl.PopupMenuShowing event handler.
' 
' You can find sample updates and versions for different programming languages here:
' http://www.devexpress.com/example=T157245

Imports System.Reflection
Imports System.Runtime.CompilerServices
Imports System.Runtime.InteropServices

' General Information about an assembly is controlled through the following 
' set of attributes. Change these attribute values to modify the information
' associated with an assembly.
<Assembly: AssemblyTitle("RTFRibbonMini")>
<Assembly: AssemblyDescription("")>
<Assembly: AssemblyConfiguration("")>
<Assembly: AssemblyCompany("")>
<Assembly: AssemblyProduct("RTFRibbonMini")>
<Assembly: AssemblyCopyright("Copyright ©  2014")>
<Assembly: AssemblyTrademark("")>
<Assembly: AssemblyCulture("")>

' Setting ComVisible to false makes the types in this assembly not visible 
' to COM components.  If you need to access a type in this assembly from 
' COM, set the ComVisible attribute to true on that type.
<Assembly: ComVisible(False)>

' The following GUID is for the ID of the typelib if this project is exposed to COM
<Assembly: Guid("507c6ecf-6acb-416f-8a1e-2ac9f153d6df")>

' Version information for an assembly consists of the following four values:
'
'      Major Version
'      Minor Version 
'      Build Number
'      Revision
'
' You can specify all the values or you can default the Build and Revision Numbers 
' by using the '*' as shown below:
' [assembly: AssemblyVersion("1.0.*")]
<Assembly: AssemblyVersion("1.0.0.0")>
<Assembly: AssemblyFileVersion("1.0.0.0")>
