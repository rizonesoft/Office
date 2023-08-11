using Rizonesoft.Office.ErrorHandling;

namespace Rizonesoft.Office.Settings
{
    /// <summary>
    /// Represents a setting stored in the registry.
    /// </summary>
    /// <typeparam name="T">The type of the setting value.</typeparam>
    public class RegistrySetting<T>
    {
        private string _name;
        private T _value;

        /// <summary>
        /// Initializes a new instance of the RegistrySetting class with a specified name, default value, and scope.
        /// </summary>
        /// <param name="name">The name of the setting.</param>
        /// <param name="defaultValue">The default value of the setting.</param>
        /// <param name="scope">The scope of the setting.</param>
        public RegistrySetting(string name, T defaultValue, RegistryOperations.SettingScope scope)
        {
            _name = name ?? throw new ArgumentNullException(nameof(name));
            Scope = scope;

            // Attempt to load the setting from the registry
            try
            {
                var loadedValue = RegistryOperations.Read(name, scope);
                _value = (T)Convert.ChangeType(loadedValue, typeof(T));
            }
            catch
            {
                _value = defaultValue;
                if (defaultValue != null) RegistryOperations.Write(name, defaultValue, scope);
            }
        }

        /// <summary>
        /// Gets or sets the name of the setting.
        /// </summary>
        public string Name
        {
            get => _name;
            set
            {
                if (string.IsNullOrWhiteSpace(value))
                {
                    throw new ArgumentException(@"Name cannot be null or whitespace", nameof(Name));
                }
                _name = value;
            }
        }

        /// <summary>
        /// Gets or sets the value of the setting.
        /// </summary>
        public T Value
        {
            get => _value;
            set
            {
                if (EqualityComparer<T>.Default.Equals(_value, value)) return;
                _value = value;
                try
                {
                    if (value != null) RegistryOperations.Write(_name, value, Scope);
                }
                catch (Exception ex)
                {
                    Serilogger.LogMessage(LogLevel.Error, "Failed to write the setting value to the registry.", ex);
                }
            }
        }

        /// <summary>
        /// Gets or sets the scope of the setting.
        /// </summary>
        public RegistryOperations.SettingScope Scope { get; set; }
    }
}
