namespace Rizonesoft.Office.Programs;

/// <summary>
/// Manages program mutexes for OfficeProgram instances.
/// </summary>
public static class ProgramMutexManager
{
    private static readonly Dictionary<OfficeProgram, string?> Mutexes = new()
    {
        { OfficeProgram.Action, "AD099093D41B48798674B0A91D075972" },
        { OfficeProgram.Assure, "A71C9423074B433A8F8166C111D9A798" },
        { OfficeProgram.Booking, "3D11BAAFFAF04AEAB9AE38391077AECC" },
        { OfficeProgram.Clock, "DC614210F76E4175A284FA0E5E7EA289" },
        { OfficeProgram.Duplicare, "AD6F8712A7734432886BBD5F26EF1C30" },
        { OfficeProgram.Evaluate, "3684ED7E332E428EB797B87A500B59AE" },
        { OfficeProgram.Filer, "453BE47311694B758E744082EBE9F85C" },
        { OfficeProgram.Flow, "E462030D095C4ABB8AD088B121B693A0" },
        { OfficeProgram.Globe, "3700106A50A64603A9CA25CAEAA19A9F" },
        { OfficeProgram.Have, "F37843D460A04A1EB012F2432471C87F" },
        { OfficeProgram.Imagine, "78B50D37F2314ECF986138D40696D570" },
        { OfficeProgram.Komplete, "1485337B2B8046D5A5E5C40E0037E970" },
        { OfficeProgram.Lead, "26D26202BE914979B677C3D6E13BC9EC" },
        { OfficeProgram.Merchant, "56E22746A2E64334A2CA094DD40625E9" },
        { OfficeProgram.Mia, "978CCD1515C44945B584822497BB3EDA" },
        { OfficeProgram.Mission, "EADB2CA0B832420C9B4782B271FDA40E" },
        { OfficeProgram.Nerve, "B64CA93527534913B11997F2E4C55498" },
        { OfficeProgram.Operate, "BC622B53340949BF83D8D871E2088D22" },
        { OfficeProgram.Qapture, "8CBA461F243D49E79179F93D4BC0B0D5" },
        { OfficeProgram.Repo, "4A85686C64DE45A9A83B34DE33A878F1" },
        { OfficeProgram.Scholar, "BBD19F856F09475DB0329AAECD49CBC5" },
        { OfficeProgram.Session, "0A171F31F7064D3EADD026F3AEB8B119" },
        { OfficeProgram.Soap, "CB2CFCEF808143DD97A2C87F2EDF4F7C" },
        { OfficeProgram.Verbum, "B8B8DF9A6E714A099CFFE17827960831" },
        { OfficeProgram.Voice, "27A17F37EAC04452AAA472CC0DBF8297" },
        { OfficeProgram.Wealth, "2C221B03FD5C408A914FCC604DE15DB6" },
        { OfficeProgram.Xhibit, "F0684AD7BD1544A08B1B57EDB7D8E750" },
        { OfficeProgram.Yield, "DD18DF48DF6F431CB136E0D5A4743819" },
        { OfficeProgram.Zone, "C19C27422BE647E8B2E73410EE2CFBEF" }
    };

    /// <summary>
    /// Retrieves the mutex for the specified OfficeProgram.
    /// </summary>
    /// <param name="officeProgram">The OfficeProgram for which to retrieve the mutex.</param>
    /// <returns>A string representing the mutex for the given OfficeProgram.</returns>
    /// <exception cref="ArgumentOutOfRangeException">Thrown when an invalid OfficeProgram is provided.</exception>
    public static string? GetProgramMutex(OfficeProgram officeProgram)
    {
        if (Mutexes.TryGetValue(officeProgram, out var mutex))
        {
            return mutex;
        }

        throw new ArgumentOutOfRangeException(nameof(officeProgram), officeProgram,
            @"Wow, an unknown OfficeProgram? That's unexpected! Did aliens add this program?");
    }
}