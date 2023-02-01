' Developer Express Code Central Example:
' How to implement the basic idea of the Microsoft Word "Format Painter" feature for RichEditControl
' 
' This example demonstrates how to copy the characters and paragraphs properties
' and apply formatting to the selected text. Try the Format Painter button on the
' ribbon Home tab.
' 
' To obtain the selected text range, the
' RichEditDocument.Document.Selection property is used. The characters and
' paragraphs properties are obtained in the BarCheckItem.CheckedChanged event
' handler. Then, they are stored in the CharacterPropertiesObject and
' ParagraphPropertiesObject object containers.
' 
' In order to change the current
' RichEditControl cursor, a MouseCursorCalculator descendant is implemented. Check
' the custom MouseCursorCalculator class Calculate method for clarification.
' 
' You can find sample updates and versions for different programming languages here:
' http://www.devexpress.com/example=E5223

Imports System.Reflection
Imports System.Runtime.CompilerServices
Imports System.Runtime.InteropServices
' General Information about an assembly is controlled through the following 
' set of attributes. Change these attribute values to modify the information
' associated with an assembly.
<Assembly: AssemblyTitle("DXApplication9")>
<Assembly: AssemblyDescription("")>
<Assembly: AssemblyConfiguration("")>
<Assembly: AssemblyCompany("")>
<Assembly: AssemblyProduct("DXApplication9")>
<Assembly: AssemblyCopyright("Copyright ©  2014")>
<Assembly: AssemblyTrademark("")>
<Assembly: AssemblyCulture("")>
' Setting ComVisible to false makes the types in this assembly not visible 
' to COM components.  If you need to access a type in this assembly from 
' COM, set the ComVisible attribute to true on that type.
<Assembly: ComVisible(False)>
' The following GUID is for the ID of the typelib if this project is exposed to COM
<Assembly: Guid("d69e93ea-1660-451a-b562-494b44c38a6d")>
' Version information for an assembly consists of the following four values:
'
'      Major Version
'      Minor Version 
'      Build Number
'      Revision
'
<Assembly: AssemblyVersion("1.0.0.0")>
<Assembly: AssemblyFileVersion("1.0.0.0")>
