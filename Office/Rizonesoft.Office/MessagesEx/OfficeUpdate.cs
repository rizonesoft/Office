using System.Xml;
using DevExpress.Utils;

namespace Rizonesoft.Office.MessagesEx
{
    /// <summary>
    /// OfficeUpdate class is responsible for checking and notifying about updates to the Office application.
    /// </summary>
    public static class OfficeUpdate
    {
        /// <summary>
        /// Checks for updates by calling GetOfficeUpdate with the provided URL.
        /// </summary>
        public static void CheckForUpdates()
        {
            GetOfficeUpdate("https://www.rizonesoft.com/update/office22.xml");
        }

        /// <summary>
        /// Retrieves update information from the provided updateXmlURL and notifies the user if an update is available.
        /// </summary>
        /// <param name="updateXmlUrl">The URL to fetch update information from.</param>
        /// <returns>Returns an empty string.</returns>
        public static string GetOfficeUpdate(string updateXmlUrl)
        {
            Version? newVersion = null;

            try
            {
                using var updateReader = new XmlTextReader(updateXmlUrl);
                updateReader.MoveToContent();

                var elementName = string.Empty;

                if (updateReader is { NodeType: XmlNodeType.Element, Name: "office" })
                {
                    while (updateReader.Read())
                    {
                        if (updateReader.NodeType == XmlNodeType.Element)
                        {
                            elementName = updateReader.Name;
                        }
                        else if (updateReader is { NodeType: XmlNodeType.Text, HasValue: true })
                        {
                            switch (elementName)
                            {
                                case "version":
                                    newVersion = new Version(updateReader.Value);
                                    break;

                                case "url":
                                    break;
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                return string.Empty;
            }

            var applicationVersion = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
            if (applicationVersion != null && (newVersion is null || applicationVersion.CompareTo(newVersion) >= 0)) return string.Empty;
            if (newVersion == null) return string.Empty;
            var sReturnVersion = $"{newVersion.Major}.{newVersion.Minor}.{newVersion.Build}";
            var updateSvgImageCollection = new SvgImageCollection();
            updateSvgImageCollection.Add("automaticupdates", "image://svgimages/dashboards/automaticupdates.svg");
            updateSvgImageCollection.Add("business_world", $"image://svgimages/icon builder/business_world.svg");

            MessageData messageData = new("Update available",
                $"We think there might be a new Office version ({sReturnVersion}) available.",
                updateSvgImageCollection[1]);
            MessageForm messageForm = new(messageData)
            {
                Opacity = 0,
                ShowInTaskbar = false
            };

            messageForm.Show();
            return string.Empty;
        }
    }
}
