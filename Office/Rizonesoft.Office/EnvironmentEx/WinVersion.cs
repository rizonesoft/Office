namespace Rizonesoft.Office.EnvironmentEx
{
    using System;

    internal struct VersionInfo
    {
        public int Major;
        public int Minor;
        public int BuildNum;
    }

    internal abstract class WinVersion
    {
        public static void GetVersion(out VersionInfo info)
        {
            var version = Environment.OSVersion.Version;
            info.Major = version.Major;
            info.Minor = version.Minor;
            info.BuildNum = version.Build;
            if (info.BuildNum >= 22000)
                info.Major = 11;
        }
        public static bool IsBuildNumGreaterOrEqual(uint buildNumber)
        {
            GetVersion(out var info);
            return buildNumber >= info.BuildNum;
        }
    }
}
