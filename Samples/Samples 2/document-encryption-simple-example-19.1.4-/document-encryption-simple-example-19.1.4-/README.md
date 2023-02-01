<!-- default file list -->
*Files to look at*:

* [Form1.cs](./CS/RichEditControl_Encryption/Form1.cs) (VB: [Form1.vb](./VB/RichEditControl_Encryption/Form1.vb))
<!-- default file list end -->

# Document Encryption (Simple Example)

The following sample project shows how to use the RichEditControl for WinForms to load and save password-encrypted files. You can specify a password and an encryption type on the left pane and export the result to DOCX or DOC format. When a user re-opens the file with a new password, the [RichEditControl.EncryptedFilePasswordRequested](https://docs.devexpress.com/WindowsForms/DevExpress.XtraRichEdit.RichEditControl.EncryptedFilePasswordRequested?v=19.1) and [RichEditControl.EncryptedFilePasswordCheckFailed](https://docs.devexpress.com/WindowsForms/DevExpress.XtraRichEdit.RichEditControl.EncryptedFilePasswordCheckFailed?v=19.1) events occur. If the user cancels the operation or exceeds the number of attempts to enter the password, RichEditControl shows an exception message.

![image](/media/project_image.png)