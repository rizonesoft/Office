Imports DevExpress.XtraRichEdit
Imports DevExpress.XtraRichEdit.API.Native
Imports System
Imports System.Collections.Generic
Imports System.ComponentModel
Imports System.Data
Imports System.Drawing
Imports System.IO
Imports System.Linq
Imports System.Text
Imports System.Threading.Tasks
Imports System.Windows.Forms
Imports DevExpress.XtraEditors

Namespace RichEditControl_Encryption
	Partial Public Class Form1
		Inherits XtraForm

		Private tryCount As Integer = 4
		Public Sub New()
			InitializeComponent()
			InitializeEncryptionComboBoxEdit1()
			InitializePasswordEdit()
			richEditControl1.LoadDocument("testEncrypted.docx")
		End Sub
		Private Sub RichEditControl1_BeforeImport(ByVal sender As Object, ByVal e As BeforeImportEventArgs) Handles richEditControl1.BeforeImport
			'Specify the password to load an encrypted file
			richEditControl1.Options.Import.EncryptionPassword = "test"
		End Sub

		Private Sub RichEditControl1_EncryptedFilePasswordRequested(ByVal sender As Object, ByVal e As EncryptedFilePasswordRequestedEventArgs) Handles richEditControl1.EncryptedFilePasswordRequested
			'Count the number of attempts to enter the password
			If tryCount > 0 Then
				tryCount -= 1
			End If
		End Sub

		Private Sub RichEditControl1_EncryptedFilePasswordCheckFailed(ByVal sender As Object, ByVal e As EncryptedFilePasswordCheckFailedEventArgs) Handles richEditControl1.EncryptedFilePasswordCheckFailed

			'Analyze the error that led to this event
			'Depending on the user input and number of attempts,
			'Prompt user to enter a password again
			'or create an empty file
			Select Case e.Error
				Case RichEditDecryptionError.PasswordRequired
					If tryCount > 0 Then
						e.TryAgain = True
						e.Handled = True
						MessageBox.Show("You did not enter the password!", String.Format(" {0} attempts left", tryCount))
					Else
						e.TryAgain = False
					End If


				Case RichEditDecryptionError.WrongPassword
					If tryCount > 0 Then
						If (MessageBox.Show("The password is incorrect. Try Again?", String.Format(" {0} attempts left", tryCount), MessageBoxButtons.YesNo)) = DialogResult.Yes Then
							e.TryAgain = True
							e.Handled = True
						End If

					End If
			End Select
 			e.Handled = True
		End Sub

		Private Sub InitializePasswordEdit()
			passwordEdit1.EditValue = "123"
		End Sub

		Private Sub InitializeEncryptionComboBoxEdit1()
			For Each currentValue As EncryptionType In System.Enum.GetValues(GetType(EncryptionType))
				encryptionComboBox1.Properties.Items.Add(currentValue.ToString())
			Next currentValue
			encryptionComboBox1.EditValue = EncryptionType.Strong.ToString()
		End Sub

		Private Sub SimpleButton1_Click(ByVal sender As Object, ByVal e As EventArgs) Handles simpleButton1.Click
			richEditControl1.Document.Encryption.Password = passwordEdit1.EditValue.ToString()
			richEditControl1.Document.Encryption.Type = DirectCast(System.Enum.Parse(GetType(EncryptionType), encryptionComboBox1.EditValue.ToString()), EncryptionType)
			richEditControl1.SaveDocumentAs()
		End Sub

		Private Sub RichEditControl1_DecryptionFailed(ByVal sender As Object, ByVal e As DecryptionFailedEventArgs) Handles richEditControl1.DecryptionFailed
			MessageBox.Show(e.Exception.Message.ToString(), "Exception")
		End Sub
	End Class
	#Region "#CustomSaveFileDialog"
	Public Class MyRichEditControl
		Inherits RichEditControl

		Public Overrides Sub SaveDocumentAs()
			Using myFileDialog As New SaveFileDialog()
				myFileDialog.Filter = "Word 2007 Document (*.docx)|*.docx|Microsoft Word Document (*.doc*)|*.doc*"
				myFileDialog.FilterIndex = 1
				myFileDialog.CheckFileExists = False
				Dim result As DialogResult = myFileDialog.ShowDialog()
				If result = DialogResult.OK Then
					Dim ext As String = Path.GetExtension(myFileDialog.FileName)
					If ext = ".docx" Then
						Me.SaveDocument(myFileDialog.FileName, DocumentFormat.OpenXml)
					Else
						Me.SaveDocument(myFileDialog.FileName, DocumentFormat.Doc)
					End If

					If MessageBox.Show("The document is saved with new password. Open the file?", "", MessageBoxButtons.YesNo) = DialogResult.Yes Then
						Me.LoadDocument(myFileDialog.FileName)
					End If
				End If
			End Using
		End Sub
	End Class
	#End Region ' #CustomSaveFileDialog
End Namespace
