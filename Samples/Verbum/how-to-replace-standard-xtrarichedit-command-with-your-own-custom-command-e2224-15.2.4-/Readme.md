<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128611024/15.2.4%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/E2224)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [Form1.cs](./CS/CustomCommand/Form1.cs) (VB: [Form1.vb](./VB/CustomCommand/Form1.vb))
<!-- default file list end -->
# How to replace standard XtraRichEdit command with your own custom command


<p>This example illustrates the technique used to modify the functionality of existing XtraRichEdit commands.<br />
The RichEditControl exposes the IRichEditCommandFactoryService interface that enables you to substitute default command with your own custom command. <br />
First, create a command class, inherited from the command that you've decided to replace. Override its methods. The main functionality and command specifics  is located in the <a href="http://documentation.devexpress.com/#CoreLibraries/DevExpressUtilsCommandsCommand_Executetopic">Execute</a> or the<strong> ExecuteCore</strong> method (the latter does not check for the command availability). <br />
Then, create a class implementing the IRichEditCommandFactoryService. You should override the CreateCommand method to create an instance of a custom command class if an identifier of a certain command is passed as a parameter. So, instead of the default command, a custom command will be used by the RichEditControl.<br />
Finally we use this class to substitute the default RichEditControl's service.</p>

<br/>


