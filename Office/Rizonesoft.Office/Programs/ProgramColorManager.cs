namespace Rizonesoft.Office.Programs;

/// <summary>
/// A utility class for managing colors for Rizonesoft Office applications.
/// </summary>
public static class ProgramColorManager
{
    /// <summary>
    /// Gets the predefined color for a given Rizonesoft Office application.
    /// </summary>
    /// <param name="officeProgram">The Rizonesoft Office application.</param>
    /// <returns>A Color representing the predefined color for the given Rizonesoft Office application.</returns>
    /// <exception cref="ArgumentOutOfRangeException">Thrown when an invalid Rizonesoft Office color is specified.</exception>
    public static Color GetPredefinedColor(OfficeProgram officeProgram)
    {
        return officeProgram switch
        {
            OfficeProgram.Action => Color.FromArgb(255, 13, 171, 182),
            OfficeProgram.Assure => Color.FromArgb(255, 123, 181, 78),
            OfficeProgram.Booking => Color.FromArgb(255, 151, 64, 143),
            OfficeProgram.Clock => Color.FromArgb(255, 11, 113, 179),
            OfficeProgram.Duplicare => Color.FromArgb(235, 235, 107, 82),
            OfficeProgram.Evaluate => Color.FromArgb(255, 19, 166, 98),
            OfficeProgram.Filer => Color.FromArgb(255, 229, 209, 50),
            OfficeProgram.Flow => Color.FromArgb(255, 244, 167, 49),
            OfficeProgram.Globe => Color.FromArgb(255, 11, 113, 179),
            OfficeProgram.Have => Color.FromArgb(255, 226, 51, 56),
            OfficeProgram.Imagine => Color.FromArgb(255, 123, 182, 76),
            OfficeProgram.Komplete => Color.FromArgb(255, 13, 171, 182),
            OfficeProgram.Lead => Color.FromArgb(255, 159, 53, 125),
            OfficeProgram.Merchant => Color.FromArgb(255, 10, 173, 182),
            OfficeProgram.Mia => Color.FromArgb(255, 245, 168, 52),
            OfficeProgram.Mission => Color.FromArgb(255, 11, 172, 182),
            OfficeProgram.Nerve => Color.FromArgb(255, 115, 63, 145),
            OfficeProgram.Operate => Color.FromArgb(255, 11, 172, 182),
            OfficeProgram.Qapture => Color.FromArgb(255, 235, 107, 82),
            OfficeProgram.Repo => Color.FromArgb(255, 229, 209, 50),
            OfficeProgram.Scholar => Color.FromArgb(255, 226,51, 56),
            OfficeProgram.Session => Color.FromArgb(255, 13, 171, 182),
            OfficeProgram.Soap => Color.FromArgb(255, 163, 78, 151),
            OfficeProgram.Verbum => Color.FromArgb(255, 12, 113, 181),
            OfficeProgram.Voice => Color.FromArgb(255, 245, 168, 52),
            OfficeProgram.Wealth => Color.FromArgb(255, 10, 173, 182),
            OfficeProgram.Xhibit => Color.FromArgb(255, 227, 209, 51),
            OfficeProgram.Yield => Color.FromArgb(255, 159, 53, 125),
            OfficeProgram.Zone => Color.FromArgb(255, 174, 77, 148),
            _ => throw new ArgumentOutOfRangeException(nameof(officeProgram), officeProgram,
                @"Invalid Rizonesoft Office color specified.")
        };

    }
}