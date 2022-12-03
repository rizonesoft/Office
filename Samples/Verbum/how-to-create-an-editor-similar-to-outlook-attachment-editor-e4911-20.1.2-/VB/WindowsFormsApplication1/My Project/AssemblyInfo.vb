' Developer Express Code Central Example:
' How to create an editor similar to Outlook Attachment Editor
' 
' This example demonstrates how the RichEditControl component can be used to
' emulate the Outlook Attachment Editor behavior.
' The main idea of the approach
' demonstrated in this sample is to use the DOCVARIABLE field
' (http://documentation.devexpress.com/#WindowsForms/CustomDocument9721) to
' display corresponding RTF content for each inserted file.
' 
' You can find sample updates and versions for different programming languages here:
' http://www.devexpress.com/example=E4911


Imports Microsoft.VisualBasic
Imports System.Reflection
Imports System.Runtime.CompilerServices
Imports System.Runtime.InteropServices

' General Information about an assembly is controlled through the following 
' set of attributes. Change these attribute values to modify the information
' associated with an assembly.
<Assembly: AssemblyTitle("WindowsFormsApplication1")>
<Assembly: AssemblyDescription("")>
<Assembly: AssemblyConfiguration("")>
<Assembly: AssemblyCompany("")>
<Assembly: AssemblyProduct("WindowsFormsApplication1")>
<Assembly: AssemblyCopyright("Copyright ©  2013")>
<Assembly: AssemblyTrademark("")>
<Assembly: AssemblyCulture("")>

' Setting ComVisible to false makes the types in this assembly not visible 
' to COM components.  If you need to access a type in this assembly from 
' COM, set the ComVisible attribute to true on that type.
<Assembly: ComVisible(False)>

' The following GUID is for the ID of the typelib if this project is exposed to COM
<Assembly: Guid("27414171-78a7-4973-ac86-83f33474856a")>

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
