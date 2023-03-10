using System;
using System.ComponentModel;
using System.Xml;
using DevExpress.Utils;
using DevExpress.XtraBars.Alerter;
using DevExpress.XtraEditors.Internal;
using static DevExpress.XtraBars.Docking.AutoHideControl;

namespace Rizonesoft.Office.MessagesEx
{
    public class OfficeUpdate
    {
        public static void CheckForUpdates()
        {
            GetOfficeUpdate("https://www.rizonesoft.com/update/office22.xml");
        }

        public static string GetOfficeUpdate(string updateXmlURL)
        {
            Version? newVersion = null;
            XmlTextReader? updateReader = null;

            try
            {
                updateReader = new XmlTextReader(updateXmlURL);
                updateReader.MoveToContent();
                string elementName = string.Empty;

                if ((updateReader.NodeType == XmlNodeType.Element) && (updateReader.Name == "office"))
                {
                    while (updateReader.Read())
                    {
                        if (updateReader.NodeType == XmlNodeType.Element)
                        {
                            elementName = updateReader.Name;
                        }
                        else
                        {
                            if ((updateReader.NodeType == XmlNodeType.Text) && (updateReader.HasValue))
                            {
                                switch (elementName)
                                {
                                    case "version":
                                        newVersion = new Version(updateReader.Value);
                                        break;

                                    case "url":
                                        string downloadUrl = updateReader.Value;
                                        break;
                                }
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
#pragma warning disable CS8602 // Dereference of a possibly null reference.
            finally
            {
                updateReader.Close();
            }

            Version? applicationVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
            if (applicationVersion.CompareTo(newVersion) < 0)
            {
                string sReturnVersion = $"{newVersion.Major}.{newVersion.Minor}.{newVersion.Build}";
                SvgImageCollection updateSVGImageCollection = new SvgImageCollection();
                updateSVGImageCollection.Add("automaticupdates", "image://svgimages/dashboards/automaticupdates.svg");
                updateSVGImageCollection.Add("business_world", "image://svgimages/icon builder/business_world.svg");

                MessageData messageData = new("Update available", "We think there might be a new Office version (" + sReturnVersion + ") available.", updateSVGImageCollection[1]);
                MessageForm messageForm = new(messageData)
                {
                    Opacity = 0,
                    ShowInTaskbar = false
                };
                messageForm.Show();

            }
#pragma warning restore CS8602 // Dereference of a possibly null reference.

            return string.Empty;
        }


    }
}
