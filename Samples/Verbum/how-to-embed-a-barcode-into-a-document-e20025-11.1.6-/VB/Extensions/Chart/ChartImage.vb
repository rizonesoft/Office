Imports Microsoft.VisualBasic
	Imports System
	Imports System.Collections.Generic
	Imports System.Linq
	Imports DevExpress.XtraRichEdit.Fields
	Imports DevExpress.XtraRichEdit.Model
	Imports System.IO
	Imports DevExpress.XtraCharts
	Imports System.Drawing.Imaging
	Imports DevExpress.XtraRichEdit.Utils
	Imports System.Text
Namespace BizPad

	Public Class ChartImage
		Private _ViewType As ViewType = ViewType.Pie

		Private Sub ParseTypeSwitches(ByVal switches As InstructionCollection)
			Dim type As String = switches.GetString("c")
			If type Is Nothing Then
				type = String.Empty
			End If
			Select Case type.ToLower()
				Case "bar"
					_ViewType = ViewType.Bar
				Case "line"
					_ViewType = ViewType.Line
				Case Else
					_ViewType = ViewType.Pie
			End Select
		End Sub

		Private _Width? As Integer = Nothing
		Private _Height? As Integer = Nothing

		Private Sub ParseSizeSwitches(ByVal switches As InstructionCollection)
			_Width = switches.GetNullableInt("w")
			_Height = switches.GetNullableInt("h")
		End Sub
		Private _Data As New List(Of KeyValuePair(Of String, Double))()

		Private Sub ParseDataSwitches(ByVal switches As InstructionCollection)
			Dim data As String = switches.GetString("d")
			If data Is Nothing Then
				data = String.Empty
			End If

			For Each t As String In data.Split(","c)
				Dim value As Double

				Dim pair() As String = t.Split("|"c)

				If pair.Length = 0 Then
					Continue For
				End If

				If pair.Length = 1 Then
					If (Not Double.TryParse(pair(0), value)) Then
						_Data.Add(New KeyValuePair(Of String, Double)(pair(0), 0))
					Else
						_Data.Add(New KeyValuePair(Of String, Double)(String.Empty, value))
					End If
				Else
					If pair.Length = 2 Then
						If (Not Double.TryParse(pair(1), value)) Then
							_Data.Add(New KeyValuePair(Of String, Double)(pair(0), 0))
						Else
							_Data.Add(New KeyValuePair(Of String, Double)(pair(0), value))
						End If
					End If
				End If
			Next t
		End Sub

		Private _ShowLegent As Boolean = False

		Private Sub ParseLegentSwitches(ByVal switches As InstructionCollection)
			_ShowLegent = switches.GetBool("l")
		End Sub

		Public Sub Initialize(ByVal switches As InstructionCollection)
			ParseDataSwitches(switches)
			ParseSizeSwitches(switches)
			ParseTypeSwitches(switches)
			ParseLegentSwitches(switches)
		End Sub

		Public Function CreateChart() As Stream

			Using chart As New ChartControl()
				If _Width.HasValue Then
					chart.Width = _Width.Value
				End If
				If _Height.HasValue Then
					chart.Height = _Height.Value
				End If

				Dim undefined As Integer = 1
				Dim stream As New MemoryStream()
				Try
					Dim series As New Series("Chart", _ViewType)
					Try
						If TypeOf series.Label Is DevExpress.XtraCharts.PieSeriesLabel Then
							CType(series.Label, DevExpress.XtraCharts.PieSeriesLabel).Position = PieSeriesLabelPosition.Inside
						End If

                        If _ViewType = ViewType.Pie Then
                            series.PointOptions.ValueNumericOptions.Format = DevExpress.XtraCharts.NumericFormat.Percent
                        End If

						If _Data Is Nothing OrElse _Data.Count = 0 Then
							series.Points.Add(New SeriesPoint("Undefined", New Double() { 1 }))
							series.PointOptions.PointView = PointView.SeriesName

						Else
							series.PointOptions.PointView = PointView.ArgumentAndValues

							For i As Integer = 0 To _Data.Count - 1

								Dim argument As String = _Data(i).Key.Trim()

								If String.IsNullOrEmpty(argument) Then
									argument = "Undefined " & undefined
									undefined += 1
								End If

								series.Points.Add(New SeriesPoint(argument, New Double() { _Data(i).Value }))
							Next i
						End If

						chart.Legend.Visible = _ShowLegent
						chart.BorderOptions.Visible = False

						chart.Series.AddRange(New Series() { series })
						series = Nothing

						chart.ExportToImage(stream, ImageFormat.Bmp)

						Return stream

					Catch
						If series IsNot Nothing Then
							series.Dispose()
						End If
						Throw
					End Try

				Catch
					If stream IsNot Nothing Then
						stream.Dispose()
					End If
					Throw
				End Try
			End Using
		End Function

		Public Function CreateImage() As RichEditImage
			Return RichEditImage.CreateImage(CreateChart())
		End Function

	End Class
End Namespace
