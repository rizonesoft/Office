Imports Microsoft.VisualBasic
Imports System
Imports System.Collections
Imports System.Collections.Generic
Imports System.Drawing
Imports System.Threading
Imports DevExpress.Utils.Text
Imports DevExpress.XtraPrinting
Imports DevExpress.XtraPrinting.BarCode
Imports DevExpress.XtraPrinting.Native
Imports DevExpress.XtraRichEdit.Fields
Imports DevExpress.XtraRichEdit.Utils
Namespace BizPad

    Public Class BarCodeImage
        Implements IBarCodeData
        Private _Width? As Integer = Nothing
        Private _Height? As Integer = Nothing

        Private Sub ParseSizeSwitches(ByVal switches As InstructionCollection)
            _Width = switches.GetNullableInt("w")
            _Height = switches.GetNullableInt("h")
        End Sub

        Private _Data As String

        Private Sub ParseDataSwitches(ByVal switches As InstructionCollection)
            _Data = switches.GetString("d")
        End Sub

        Private _ShowLabel As Boolean = False

        Private Sub ParseShowLabelSwitches(ByVal switches As InstructionCollection)
            _ShowLabel = switches.GetBool("l")
        End Sub

        Private _Module As Double = 0.0R

        Private Sub ParseModuleSize(ByVal switches As InstructionCollection)
            Dim k As String = switches.GetString("k")
            If (Not String.IsNullOrWhiteSpace(k)) Then
                Dim d As Double = 0.0R
                If (Not Double.TryParse(k.Trim(), d)) Then
                    d = 0.0R
                End If
                _Module = d
            End If
        End Sub

        Private _generator As IBarCodeGenerator
        Private ReadOnly Property Generator() As IBarCodeGenerator
            Get
                Return _generator
            End Get
        End Property

        Private Sub InitializeGenerator(ByVal switches As InstructionCollection)
            _generator = BarCodeGeneratorFactory.Create(switches.GetString("t"), switches)
        End Sub

        Public Sub Initialize(ByVal switches As InstructionCollection)
            ParseDataSwitches(switches)
            ParseSizeSwitches(switches)
            ParseShowLabelSwitches(switches)
            ParseModuleSize(switches)
            InitializeGenerator(switches)
        End Sub

        Private Class GraphicsHelper
            Implements IGraphics
            Private _gr As Graphics

            Public Sub New(ByVal gr As Graphics)
                If gr Is Nothing Then
                    Throw New ArgumentNullException("gr", "gr is null.")
                End If
                _gr = gr
            End Sub

            Private Sub Dispose() Implements IDisposable.Dispose
                Dim brushes As Dictionary(Of Color, Brush) = Interlocked.Exchange(Of Dictionary(Of Color, Brush))(_Brushes, Nothing)
                If brushes IsNot Nothing Then
                    For Each k As KeyValuePair(Of Color, Brush) In brushes
                        k.Value.Dispose()
                    Next k
                End If
                Dim pens As Dictionary(Of Color, Pen) = Interlocked.Exchange(Of Dictionary(Of Color, Pen))(_Pens, Nothing)
                If pens IsNot Nothing Then
                    For Each k As KeyValuePair(Of Color, Pen) In pens
                        k.Value.Dispose()
                    Next k
                End If
            End Sub

            Private ReadOnly Property Dpi() As Single Implements IGraphics.Dpi
                Get
                    Throw New NotImplementedException()
                End Get
            End Property

            Private Function GetPageCount(ByVal basePageNumber As Integer, ByVal continuousPageNumbering As DevExpress.Utils.DefaultBoolean) As Integer Implements IGraphics.GetPageCount
                Throw New NotImplementedException()
            End Function

            Private Sub ResetDrawingPage() Implements IGraphics.ResetDrawingPage
                Throw New NotImplementedException()
            End Sub

            Private Sub SetDrawingPage(ByVal page As Page) Implements IGraphics.SetDrawingPage
                Throw New NotImplementedException()
            End Sub

            Private Sub ApplyTransformState(ByVal order As System.Drawing.Drawing2D.MatrixOrder, ByVal removeState As Boolean) Implements IGraphicsBase.ApplyTransformState
                Throw New NotImplementedException()
            End Sub

            Private Property ClipBounds() As RectangleF Implements IGraphicsBase.ClipBounds
                Get
                    Throw New NotImplementedException()
                End Get
                Set(ByVal value As RectangleF)
                    Throw New NotImplementedException()
                End Set
            End Property

            Private Sub DrawCheckBox(ByVal rect As RectangleF, ByVal state As System.Windows.Forms.CheckState) Implements IGraphicsBase.DrawCheckBox
                Throw New NotImplementedException()
            End Sub

            Private Sub DrawEllipse(ByVal pen As Pen, ByVal x As Single, ByVal y As Single, ByVal width As Single, ByVal height As Single) Implements IGraphicsBase.DrawEllipse
                Throw New NotImplementedException()
            End Sub

            Private Sub DrawEllipse(ByVal pen As Pen, ByVal rect As RectangleF) Implements IGraphicsBase.DrawEllipse
                Throw New NotImplementedException()
            End Sub

            Private Sub DrawImage(ByVal image As Image, ByVal point As Point) Implements IGraphicsBase.DrawImage
                Throw New NotImplementedException()
            End Sub

            Private Sub DrawImage(ByVal image As Image, ByVal rect As RectangleF, ByVal underlyingColor As Color) Implements IGraphicsBase.DrawImage
                Throw New NotImplementedException()
            End Sub

            Private Sub DrawImage(ByVal image As Image, ByVal rect As RectangleF) Implements IGraphicsBase.DrawImage
                Throw New NotImplementedException()
            End Sub

            Private Sub DrawLine(ByVal pen As Pen, ByVal x1 As Single, ByVal y1 As Single, ByVal x2 As Single, ByVal y2 As Single) Implements IGraphicsBase.DrawLine
                Throw New NotImplementedException()
            End Sub

            Private Sub DrawLine(ByVal pen As Pen, ByVal pt1 As PointF, ByVal pt2 As PointF) Implements IGraphicsBase.DrawLine
                Throw New NotImplementedException()
            End Sub

            Private Sub DrawLines(ByVal pen As Pen, ByVal points() As PointF) Implements IGraphicsBase.DrawLines
                Throw New NotImplementedException()
            End Sub

            Private Sub DrawPath(ByVal pen As Pen, ByVal path As System.Drawing.Drawing2D.GraphicsPath) Implements IGraphicsBase.DrawPath
                Throw New NotImplementedException()
            End Sub

            Public Sub DrawRectangle(ByVal pen As Pen, ByVal bounds As RectangleF) Implements IGraphics.DrawRectangle
                _gr.DrawRectangle(pen, bounds.X, bounds.Y, bounds.Width, bounds.Height)
            End Sub

            Private Sub DrawString(ByVal s As String, ByVal font As Font, ByVal brush As Brush, ByVal point As PointF) Implements IGraphicsBase.DrawString
                _gr.DrawString(s, font, brush, point)
            End Sub

            Private Sub DrawString(ByVal s As String, ByVal font As Font, ByVal brush As Brush, ByVal point As PointF, ByVal format As StringFormat) Implements IGraphicsBase.DrawString
                _gr.DrawString(s, font, brush, point, format)
            End Sub

            Private Sub DrawString(ByVal s As String, ByVal font As Font, ByVal brush As Brush, ByVal bounds As RectangleF) Implements IGraphicsBase.DrawString
                _gr.DrawString(s, font, brush, bounds)
            End Sub

            Private Sub DrawString(ByVal s As String, ByVal font As Font, ByVal brush As Brush, ByVal bounds As RectangleF, ByVal format As StringFormat) Implements IGraphicsBase.DrawString
                _gr.DrawString(s, font, brush, bounds, format)
            End Sub

            Private Sub FillEllipse(ByVal brush As Brush, ByVal x As Single, ByVal y As Single, ByVal width As Single, ByVal height As Single) Implements IGraphicsBase.FillEllipse
                Throw New NotImplementedException()
            End Sub

            Private Sub FillEllipse(ByVal brush As Brush, ByVal rect As RectangleF) Implements IGraphicsBase.FillEllipse
                Throw New NotImplementedException()
            End Sub

            Private Sub FillPath(ByVal brush As Brush, ByVal path As System.Drawing.Drawing2D.GraphicsPath) Implements IGraphicsBase.FillPath
                Throw New NotImplementedException()
            End Sub

            Private Sub FillRectangle(ByVal brush As Brush, ByVal x As Single, ByVal y As Single, ByVal width As Single, ByVal height As Single) Implements IGraphicsBase.FillRectangle
                _gr.FillRectangle(brush, x, y, width, height)
            End Sub

            Private Sub FillRectangle(ByVal brush As Brush, ByVal bounds As RectangleF) Implements IGraphicsBase.FillRectangle
                _gr.FillRectangle(brush, bounds)
            End Sub

            Private _Brushes As New Dictionary(Of Color, Brush)()

            Private Function GetBrush(ByVal color As Color) As Brush Implements IGraphicsBase.GetBrush
                Dim brush As Brush

                brush = Nothing

                If _Brushes.TryGetValue(color, brush) Then
                    Return brush
                End If
                _Brushes(color) = New SolidBrush(color)
                Return _Brushes(color)
            End Function

            Private _Pens As New Dictionary(Of Color, Pen)()

            Public Function GetPen(ByVal color As Color) As Pen
                Dim Pen As Pen

                Pen = Nothing

                If _Pens.TryGetValue(color, Pen) Then
                    Return Pen
                End If
                _Pens(color) = New Pen(color)
                Return _Pens(color)
            End Function

            Private Property PageUnit() As GraphicsUnit Implements IGraphicsBase.PageUnit
                Get
                    Throw New NotImplementedException()
                End Get
                Set(ByVal value As GraphicsUnit)
                    Throw New NotImplementedException()
                End Set
            End Property

            Private Sub ResetTransform() Implements IGraphicsBase.ResetTransform
                Throw New NotImplementedException()
            End Sub

            Private Sub RotateTransform(ByVal angle As Single, ByVal order As System.Drawing.Drawing2D.MatrixOrder) Implements IGraphicsBase.RotateTransform
                Throw New NotImplementedException()
            End Sub

            Private Sub RotateTransform(ByVal angle As Single) Implements IGraphicsBase.RotateTransform
                Throw New NotImplementedException()
            End Sub

            Private Sub SaveTransformState() Implements IGraphicsBase.SaveTransformState
                Throw New NotImplementedException()
            End Sub

            Private Sub ScaleTransform(ByVal sx As Single, ByVal sy As Single, ByVal order As System.Drawing.Drawing2D.MatrixOrder) Implements IGraphicsBase.ScaleTransform
                Throw New NotImplementedException()
            End Sub

            Private Sub ScaleTransform(ByVal sx As Single, ByVal sy As Single) Implements IGraphicsBase.ScaleTransform
                Throw New NotImplementedException()
            End Sub

            Private Property SmoothingMode() As System.Drawing.Drawing2D.SmoothingMode Implements IGraphicsBase.SmoothingMode
                Get
                    Throw New NotImplementedException()
                End Get
                Set(ByVal value As System.Drawing.Drawing2D.SmoothingMode)
                    Throw New NotImplementedException()
                End Set
            End Property

            Private Sub TranslateTransform(ByVal dx As Single, ByVal dy As Single, ByVal order As System.Drawing.Drawing2D.MatrixOrder) Implements IGraphicsBase.TranslateTransform
                Throw New NotImplementedException()
            End Sub

            Private Sub TranslateTransform(ByVal dx As Single, ByVal dy As Single) Implements IGraphicsBase.TranslateTransform
                Throw New NotImplementedException()
            End Sub

            Private ReadOnly Property DrawingPage() As Page Implements IPrintingSystemContext.DrawingPage
                Get
                    Throw New NotImplementedException()
                End Get
            End Property

            Private Shared measurer_Renamed As Measurer
            Private ReadOnly Property Measurer() As DevExpress.XtraPrinting.Native.Measurer Implements IPrintingSystemContext.Measurer
                Get
                    If measurer_Renamed Is Nothing Then
                        measurer_Renamed = New GdiPlusMeasurer()
                    End If
                    Return measurer_Renamed
                End Get
            End Property

            Private ReadOnly Property IPrintingSystemContext_PrintingSystem() As PrintingSystemBase Implements IPrintingSystemContext.PrintingSystem
                Get
                    Throw New NotImplementedException()
                End Get
            End Property

            Private Function GetService(ByVal serviceType As Type) As Object Implements IServiceProvider.GetService
                Throw New NotImplementedException()
            End Function

        End Class

        Private Shared Function CalcAutoModuleX(ByVal generator As IBarCodeGenerator, ByVal data As IBarCodeData, ByVal clientBounds As RectangleF) As Double
            Dim barCodeWidth As Single = clientBounds.Width
            Return CDbl(barCodeWidth) / CDbl(generator.CalcBarCodeWidth(data.Pattern))
        End Function

        Private Shared Function CalcAutoModuleY(ByVal generator As IBarCodeGenerator, ByVal data As IBarCodeData, ByVal clientBounds As RectangleF) As Double
            Dim barCodeHeight As Single = clientBounds.Height
            Return CDbl(barCodeHeight) / CDbl(generator.CalcBarCodeHeight(data.Pattern))
        End Function

        Public Function CreateBarCode() As Image
            Dim width As Integer = 100
            If _Width.HasValue AndAlso _Width.Value > 0 Then
                width = _Width.Value
            End If

            Dim height As Integer = 45
            If _Height.HasValue AndAlso _Height.Value > 0 Then
                height = _Height.Value
            End If

            Dim image As Image = New Bitmap(width, height)
            Try
                Using gr As Graphics = Graphics.FromImage(image)

                    Using helper As New GraphicsHelper(gr)

                        CType(helper, IGraphics).FillRectangle(Brushes.White, 0, 0, width, height)

                        Dim size As SizeF = TextUtils.GetStringSize(gr, _Data, (CType(Me, IBarCodeData)).Style.Font)

                        Dim barBounds As New RectangleF(0, 0, width, height - size.Height - 1)

                        Dim textBounds As New RectangleF(0, barBounds.Height + 1, barBounds.Width, size.Height)

                        If (Not Generator.SupressAutoTextAlignment()) Then

                            textBounds = New RectangleF((width \ 2) - (size.Width / 2), barBounds.Height + 1, width, size.Height)
                        End If

                        Dim ModuleX As Single = CSng(_Module)
                        If ModuleX <= 0.001 Then
                            ModuleX = CSng(CalcAutoModuleX(Generator, Me, barBounds))
                        End If

                        Dim ModuleY As Single = CSng(_Module)
                        If ModuleY <= 0.001 Then
                            ModuleY = CSng(CalcAutoModuleY(Generator, Me, barBounds))
                        End If

                        Generator.DrawBarCode(helper, barBounds, textBounds, Me, ModuleX, ModuleY)

                    End Using
                End Using

            Catch e As Exception
                If TypeOf e Is StackOverflowException OrElse TypeOf e Is OutOfMemoryException OrElse TypeOf e Is ThreadAbortException Then
                    Throw
                End If

                Using gr As Graphics = Graphics.FromImage(image)

                    gr.FillRectangle(Brushes.White, 0, 0, width, height)
                    gr.DrawRectangle(Pens.Red, 0, 0, width, height)

                End Using

            End Try

            Return image

        End Function

        Public Function CreateImage() As RichEditImage
            Return RichEditImage.CreateImage(CreateBarCode())
        End Function


        Private ReadOnly Property IBarCodeData_Alignment() As TextAlignment Implements IBarCodeData.Alignment
            Get
                Return TextAlignment.BottomCenter
            End Get
        End Property

        Private ReadOnly Property AutoModule() As Boolean Implements IBarCodeData.AutoModule
            Get
                Return False
            End Get
        End Property

        Public ReadOnly Property Text() As String
            Get
                Return _Data
            End Get
        End Property

        Private ReadOnly Property DisplayText() As String Implements IBarCodeData.DisplayText
            Get
                Return Generator.MakeDisplayText((CType(Me, IBarCodeData)).FinalText)
            End Get
        End Property
        Private ReadOnly Property FinalText() As String Implements IBarCodeData.FinalText
            Get
                If Generator.IsValidText(Text) Then
                    Return Generator.FormatText(Text)
                End If
                Return Text
            End Get
        End Property

        Private ReadOnly Property Pattern() As ArrayList Implements IBarCodeData.Pattern
            Get
                If Generator.IsValidText(Text) Then
                    Return Generator.MakeBarCodePattern((CType(Me, IBarCodeData)).FinalText)
                End If
                Return New ArrayList()
            End Get
        End Property

        Public ReadOnly Property [Module]() As Double Implements IBarCodeData.[Module]
            Get
                Return _Module
            End Get
        End Property

        Private ReadOnly Property IBarCodeData_Orientation() As BarCodeOrientation Implements IBarCodeData.Orientation
            Get
                Return BarCodeOrientation.Normal
            End Get
        End Property

        Private ReadOnly Property ShowText() As Boolean Implements IBarCodeData.ShowText
            Get
                Return _ShowLabel
            End Get
        End Property

        Private _Style As BrickStyle
        Private ReadOnly Property IBarCodeData_Style() As BrickStyle Implements IBarCodeData.Style
            Get
                If _Style Is Nothing Then
                    _Style = BrickStyle.CreateDefault()
                End If
                Return _Style
            End Get
        End Property
    End Class
End Namespace
