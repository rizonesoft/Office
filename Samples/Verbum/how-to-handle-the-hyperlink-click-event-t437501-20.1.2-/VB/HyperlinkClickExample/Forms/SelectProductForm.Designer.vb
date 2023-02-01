Namespace HyperlinkClickExample.Forms
    Partial Public Class SelectProductForm
        ''' <summary>
        ''' Required designer variable.
        ''' </summary>
        Private components As System.ComponentModel.IContainer = Nothing

        ''' <summary>
        ''' Clean up any resources being used.
        ''' </summary>
        ''' <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        Protected Overrides Sub Dispose(ByVal disposing As Boolean)
            If disposing AndAlso (components IsNot Nothing) Then
                components.Dispose()
            End If
            MyBase.Dispose(disposing)
        End Sub

        #Region "Windows Form Designer generated code"

        ''' <summary>
        ''' Required method for Designer support - do not modify
        ''' the contents of this method with the code editor.
        ''' </summary>
        Private Sub InitializeComponent()
            Me.listBoxControl = New DevExpress.XtraEditors.ListBoxControl()
            DirectCast(Me.listBoxControl, System.ComponentModel.ISupportInitialize).BeginInit()
            Me.SuspendLayout()
            ' 
            ' listBoxControl
            ' 
            Me.listBoxControl.Cursor = System.Windows.Forms.Cursors.Default
            Me.listBoxControl.Dock = System.Windows.Forms.DockStyle.Fill
            Me.listBoxControl.Location = New System.Drawing.Point(0, 0)
            Me.listBoxControl.Name = "listBoxControl"
            Me.listBoxControl.Size = New System.Drawing.Size(268, 248)
            Me.listBoxControl.TabIndex = 0
            ' 
            ' SelectProductForm
            ' 
            Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
            Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
            Me.AutoSize = True
            Me.ClientSize = New System.Drawing.Size(268, 248)
            Me.Controls.Add(Me.listBoxControl)
            Me.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedToolWindow
            Me.KeyPreview = True
            Me.MaximizeBox = False
            Me.Name = "SelectProductForm"
            Me.ShowIcon = False
            Me.ShowInTaskbar = False
            Me.StartPosition = System.Windows.Forms.FormStartPosition.Manual
            Me.Text = "Select a Product:"
            DirectCast(Me.listBoxControl, System.ComponentModel.ISupportInitialize).EndInit()
            Me.ResumeLayout(False)

        End Sub

        #End Region

        Private WithEvents listBoxControl As DevExpress.XtraEditors.ListBoxControl
    End Class
End Namespace