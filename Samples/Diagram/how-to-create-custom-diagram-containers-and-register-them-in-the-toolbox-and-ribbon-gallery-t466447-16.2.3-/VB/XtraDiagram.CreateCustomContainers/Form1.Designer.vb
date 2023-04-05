Namespace XtraDiagram.CreateCustomContainers
    Partial Public Class Form1
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

        Private Sub InitializeComponent()
            Me.diagramControl1 = New DevExpress.XtraDiagram.DiagramControl()
            Me.toolboxControl1 = New DevExpress.XtraToolbox.ToolboxControl()
            Me.ribbonControl1 = New DevExpress.XtraBars.Ribbon.RibbonControl()
            Me.splitContainerControl1 = New DevExpress.XtraEditors.SplitContainerControl()
            DirectCast(Me.diagramControl1, System.ComponentModel.ISupportInitialize).BeginInit()
            DirectCast(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).BeginInit()
            DirectCast(Me.splitContainerControl1, System.ComponentModel.ISupportInitialize).BeginInit()
            Me.splitContainerControl1.SuspendLayout()
            Me.SuspendLayout()
            ' 
            ' diagramControl1
            ' 
            Me.diagramControl1.Dock = System.Windows.Forms.DockStyle.Fill
            Me.diagramControl1.Location = New System.Drawing.Point(0, 0)
            Me.diagramControl1.Name = "diagramControl1"
            Me.diagramControl1.OptionsView.CanvasSizeMode = DevExpress.Diagram.Core.CanvasSizeMode.None
            Me.diagramControl1.OptionsView.PageSize = New System.Drawing.SizeF(800F, 600F)
            Me.diagramControl1.OptionsBehavior.SelectedStencils = New DevExpress.Diagram.Core.StencilCollection(New String(){})
            Me.diagramControl1.Size = New System.Drawing.Size(1040, 757)
            Me.diagramControl1.TabIndex = 0
            Me.diagramControl1.Text = "diagramControl1"
            Me.diagramControl1.Toolbox = Me.toolboxControl1
            ' 
            ' toolboxControl1
            ' 
            Me.toolboxControl1.Caption = "Shapes"
            Me.toolboxControl1.Dock = System.Windows.Forms.DockStyle.Fill
            Me.toolboxControl1.Location = New System.Drawing.Point(0, 0)
            Me.toolboxControl1.Name = "toolboxControl1"
            Me.toolboxControl1.OptionsBehavior.ItemSelectMode = DevExpress.XtraToolbox.ToolboxItemSelectMode.Single
            Me.toolboxControl1.OptionsView.ItemImageSize = New System.Drawing.Size(32, 32)
            Me.toolboxControl1.OptionsView.MenuButtonCaption = "More Shapes"
            Me.toolboxControl1.OptionsView.ShowToolboxCaption = True
            Me.toolboxControl1.Size = New System.Drawing.Size(276, 757)
            Me.toolboxControl1.TabIndex = 0
            Me.toolboxControl1.Text = "Shapes"
            ' 
            ' ribbonControl1
            ' 
            Me.ribbonControl1.ExpandCollapseItem.Id = 0
            Me.ribbonControl1.Items.AddRange(New DevExpress.XtraBars.BarItem() { Me.ribbonControl1.ExpandCollapseItem})
            Me.ribbonControl1.Location = New System.Drawing.Point(0, 0)
            Me.ribbonControl1.MaxItemId = 1
            Me.ribbonControl1.Name = "ribbonControl1"
            Me.ribbonControl1.Size = New System.Drawing.Size(1321, 49)
            ' 
            ' splitContainerControl1
            ' 
            Me.splitContainerControl1.Dock = System.Windows.Forms.DockStyle.Fill
            Me.splitContainerControl1.Location = New System.Drawing.Point(0, 49)
            Me.splitContainerControl1.Name = "splitContainerControl1"
            Me.splitContainerControl1.Panel1.Controls.Add(Me.toolboxControl1)
            Me.splitContainerControl1.Panel1.Text = "Panel1"
            Me.splitContainerControl1.Panel2.Controls.Add(Me.diagramControl1)
            Me.splitContainerControl1.Panel2.Text = "Panel2"
            Me.splitContainerControl1.Size = New System.Drawing.Size(1321, 757)
            Me.splitContainerControl1.SplitterPosition = 276
            Me.splitContainerControl1.TabIndex = 2
            Me.splitContainerControl1.Text = "splitContainerControl1"
            ' 
            ' Form1
            ' 
            Me.AutoScaleDimensions = New System.Drawing.SizeF(6F, 13F)
            Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
            Me.ClientSize = New System.Drawing.Size(1321, 806)
            Me.Controls.Add(Me.splitContainerControl1)
            Me.Controls.Add(Me.ribbonControl1)
            Me.Name = "Form1"
            Me.Ribbon = Me.ribbonControl1
            Me.Text = "Form1"
            DirectCast(Me.diagramControl1, System.ComponentModel.ISupportInitialize).EndInit()
            DirectCast(Me.ribbonControl1, System.ComponentModel.ISupportInitialize).EndInit()
            DirectCast(Me.splitContainerControl1, System.ComponentModel.ISupportInitialize).EndInit()
            Me.splitContainerControl1.ResumeLayout(False)
            Me.ResumeLayout(False)
            Me.PerformLayout()

        End Sub

        #End Region
        Private ribbonControl1 As DevExpress.XtraBars.Ribbon.RibbonControl
        Private splitContainerControl1 As DevExpress.XtraEditors.SplitContainerControl
        Private diagramControl1 As DevExpress.XtraDiagram.DiagramControl
        Private toolboxControl1 As DevExpress.XtraToolbox.ToolboxControl
    End Class
End Namespace

