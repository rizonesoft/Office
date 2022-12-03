<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128610249/13.1.4%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/E4438)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [Form1.cs](./CS/Form1.cs) (VB: [Form1.vb](./VB/Form1.vb))
* [Program.cs](./CS/Program.cs) (VB: [Program.vb](./VB/Program.vb))
<!-- default file list end -->
# How to export the RichEditControl document into an Outlook mail item


<p>We have the <a href="https://www.devexpress.com/Support/Center/p/E2216">Building a mail application with the RichEditControl</a> example that illustrates how to create a self-contained email client application based on our <a href="http://documentation.devexpress.com/#WindowsForms/CustomDocument6975"><u>RichEditControl</u></a>. Note that only the <strong>System.Net.Mail</strong> functionality is used in this example and the message is sent directly from the RichEditControl. However, in some scenarios (e.g., see <a href="https://www.devexpress.com/Support/Center/p/Q423631">Opening XtraRichEdit in Outlook</a>), you might wish just to transfer the RichEditControl document into Outlook. In this case, use <a href="http://msdn.microsoft.com/en-us/library/office/bb652780.aspx"><u>Outlook Interop API</u></a> to prepare a mail item based on the RichEditControl content. Process images via a custom <a href="http://documentation.devexpress.com/#CoreLibraries/clsDevExpressXtraRichEditServicesIUriProvidertopic"><u>IUriProvider Interface</u></a> implementor. Convert native RichEdit images into Outlook mail item attachments. Refer to the following web articles to learn how to deal with the Outlook-related part of this solution:</p><p><a href="http://social.msdn.microsoft.com/Forums/en-US/vsto/thread/6c063b27-7e8a-4963-ad5f-ce7e5ffb2c64/"><u>how to embed image in html body in c# into outlook mail</u></a><br />
<a href="http://social.msdn.microsoft.com/Forums/pl/outlookdev/thread/17efe46b-18fe-450f-9f6e-d8bb116161d8"><u>Attach stream data with Outlook mail client</u></a><br />
<a href="http://stackoverflow.com/questions/4312687/how-to-embed-images-in-email"><u>How to embed images in email</u></a></p>

<br/>


