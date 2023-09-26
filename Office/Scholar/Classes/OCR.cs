using System;
using System.IO;

namespace Rizonesoft.Office.Scholar.Classes
{
    public class OCR
    {
        public static byte[] PerformOCRTesseract(byte[] image)
        {
            // Specify that Tesseract use three 3 languages: English, Russian and Vietnamese.
            //string tesseractLanguages = "rus+eng+vie";
            string tesseractLanguages = "eng";

            // A path to a folder which contains languages data files and font file "pdf.ttf".
            // Language data files can be found here:
            // Good and fast: https://github.com/tesseract-ocr/tessdata_fast
            // or
            // Best and slow: https://github.com/tesseract-ocr/tessdata_best
            // Also this folder must have write permissions.
            string tesseractData = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "tesdata");

            // A path for a temporary PDF file (because Tesseract returns OCR result as PDF document)
            // string tempFile = Path.Combine(tesseractData, Path.GetRandomFileName());
            string tempFile = Path.GetTempFileName();

            bool skipImages = true;

            try
            {
                using (Tesseract.IResultRenderer renderer = Tesseract.PdfResultRenderer.CreatePdfRenderer(tempFile, tesseractData, skipImages))
                {
                    using (renderer.BeginDocument("Serachablepdf"))
                    {
                        using (Tesseract.TesseractEngine engine = new Tesseract.TesseractEngine(tesseractData, tesseractLanguages, Tesseract.EngineMode.Default))
                        {
                            engine.DefaultPageSegMode = Tesseract.PageSegMode.Auto;
                            using (MemoryStream msImg = new MemoryStream(image))
                            {
                                System.Drawing.Image imgWithText = System.Drawing.Image.FromStream(msImg);
                                for (int i = 0; i < imgWithText.GetFrameCount(System.Drawing.Imaging.FrameDimension.Page); i++)
                                {
                                    imgWithText.SelectActiveFrame(System.Drawing.Imaging.FrameDimension.Page, i);
                                    using (MemoryStream ms = new MemoryStream())
                                    {
                                        imgWithText.Save(ms, System.Drawing.Imaging.ImageFormat.Png);
                                        byte[] imgBytes = ms.ToArray();
                                        using (Tesseract.Pix img = Tesseract.Pix.LoadFromMemory(imgBytes))
                                        {
                                            using (var page = engine.Process(img, "Serachablepdf"))
                                            {
                                                renderer.AddPage(page);
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                return File.ReadAllBytes(tempFile + ".pdf");
            }
            catch (Exception e)
            {
                Console.WriteLine();
                Console.WriteLine("Please be sure that you have Language data files (*.traineddata) in your folder \"tessdata\"");
                Console.WriteLine("The Language data files can be download from here: https://github.com/tesseract-ocr/tessdata_fast");
                Console.ReadKey();
                throw new Exception("Error Tesseract: " + e.Message);
            }
            finally
            {
                if (File.Exists(tempFile + ".pdf"))
                    File.Delete(tempFile + ".pdf");
            }
        }
    }
}
