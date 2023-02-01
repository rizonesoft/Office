using System;
using System.IO;
using System.Drawing;
using System.Text.RegularExpressions;
using System.Runtime.Serialization.Formatters.Binary;
using System.Runtime.Serialization;
using System.Diagnostics;
using System.Windows.Forms;
using System.Reflection;


namespace Rizonesoft.Verbum.Configuration
{
    /// <summary>
    /// AppConfig is used for loading and saving the configuration. All public fields
    /// in this class are serialized with the BinaryFormatter and then saved to the
    /// config file. After loading the values from file, SetDefaults iterates over
    /// all public fields an sets fields set to null to the default value.
    /// </summary>
    [Serializable]
    class AppConfig
    {
        private static string acFilename = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), @"Rizonesoft\Verbum\Configuration.bin");
        private static AppConfig acInstance = null;

        // the configuration part - all public vars are stored in the config file
        // don't use "null" and "0" as default value!

        public string applicationSkin = "VS2010";
        public Size? windowSize = new Size(900, 600);
        public string spellingCulture = "en-ZA";

        /// <summary>
        /// a private constructor because this is a singleton
        /// </summary>
        private AppConfig()
        {
        }

        /// <summary>
        /// get an instance of AppConfig
        /// </summary>
        /// <returns></returns>
        public static AppConfig GetInstance()
        {
            if (acInstance == null)
            {
                acInstance = Load();
            }
            return acInstance;
        }

        /// <summary>
        /// loads the configuration from the config file
        /// </summary>
        /// <returns>an instance of AppConfig with all values set from the config file</returns>
        private static AppConfig Load()
        {
            AppConfig conf;
            CheckConfigFile();
            Stream s = null;
            try
            {
                s = File.Open(acFilename, FileMode.Open);
                BinaryFormatter b = new BinaryFormatter();
                conf = (AppConfig)b.Deserialize(s);
                s.Close();
                conf.SetDefaults();
                return conf;
            }
            catch (SerializationException)
            {
                if (s != null)
                {
                    s.Close();
                }
                AppConfig config = new AppConfig();
                config.Store();
                return config;
            }
            catch (Exception)
            {
                MessageBox.Show("Could not load Verbum's configuration file. Please check access permissions for '" + acFilename + "'.\n", "Error");
                Process.GetCurrentProcess().Kill();
            }
            return null;

        }

        /// <summary>
        /// Checks for the existence of a configuration file.
        /// First in greenshot's Applicationdata folder (where it is stored since 0.6),
        /// then (if it cannot be found there) in greenshot's program directory (where older 
        /// versions might have stored it).
        /// If the latter is the case, the file is moved to the new location, so that a user does not lose
        /// their configuration after upgrading. 
        /// If there is no file in both locations, a virgin config file is created.
        /// </summary>
        private static void CheckConfigFile()
        {
            if (!File.Exists(acFilename))
            {
                Directory.CreateDirectory(acFilename.Substring(0, acFilename.LastIndexOf(@"\")));
                new AppConfig().Store();
            }
        }

        /// <summary>
        /// saves the configuration values to the config file
        /// </summary>
        public void Store()
        {
            Stream s = File.Open(acFilename, FileMode.Create);
            BinaryFormatter formatter = new BinaryFormatter();
            formatter.Serialize(s, this);
            s.Close();
        }


        /// <summary>
        /// when new fields are added to this class, they are instanced
        /// with null by default. this method iterates over all public
        /// fields and uses reflection to set them to the proper default value.
        /// </summary>
        public void SetDefaults()
        {
            Type type = this.GetType();
            FieldInfo[] fieldInfos = type.GetFields();
            foreach (FieldInfo fi in fieldInfos)
            {
                object o = fi.GetValue(this);
                int i;
                if (o == null || (int.TryParse(o.ToString(), out i) && i == 0))
                {
                    // found field with value null. setting to default.
                    AppConfig tmpConf = new AppConfig();
                    Type tmpType = tmpConf.GetType();
                    FieldInfo defaultField = tmpType.GetField(fi.Name);
                    fi.SetValue(this, defaultField.GetValue(tmpConf));
                }
            }
        }	
    }
}