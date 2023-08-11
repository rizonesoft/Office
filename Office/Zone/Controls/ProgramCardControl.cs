using System;
using System.Drawing;
using System.Windows.Forms;
using DevExpress.Skins;
using DevExpress.Utils.Svg;

namespace Rizonesoft.Office.Zone.Controls;

/// <summary>
/// Represents a custom user control that displays information about a program and allows creating or removing a desktop shortcut.
/// </summary>
public sealed partial class ProgramCardControl : DevExpress.XtraEditors.XtraUserControl
{
    private Color _borderColor;
    private Color _hoverBorderColor = Color.FromArgb(255, 0, 94, 168);
    private readonly Cursor _defaultCursor;

    // Declare a delegate for the custom event
    public delegate void ProgramCardClickEventHandler(object sender, EventArgs e);
    // Declare the custom event using the delegate
    public event ProgramCardClickEventHandler ProgramCardClicked;

    /// <summary>
    /// Initializes a new instance of the <see cref="ProgramCardControl"/> class.
    /// </summary>
    public ProgramCardControl()
    {
        InitializeComponent();

        groupProgram.MouseEnter += GroupProgram_MouseEnter;
        groupProgram.MouseLeave += GroupProgram_MouseLeave;
        labelProgram.MouseEnter += LabelProgram_MouseEnter;
        labelProgram.MouseLeave += LabelProgram_MouseLeave;

        _defaultCursor = Cursor;
    }

    // Call this method to raise the custom event
    private void OnProgramCardClicked(EventArgs e)
    {
        ProgramCardClicked?.Invoke(this, e);
    }

    private void ProgramControl_Load(object sender, EventArgs e)
    {
        // Set the initial border color
        _borderColor = DefaultGroupBorderColor;
    }

    private void GroupControl1_Paint(object sender, PaintEventArgs e)
    {
        Rectangle rect = groupProgram.ClientRectangle;
        rect.Width -= 1;
        rect.Height -= 1;
        using var pen = new Pen(_borderColor);
        e.Graphics.DrawRectangle(pen, rect);
    }

    private void LabelProgram_MouseEnter(object sender, EventArgs e)
    {

        Cursor = Cursors.Hand;
        GroupProgram_MouseEnter(sender, e);
    }

    private void LabelProgram_MouseLeave(object sender, EventArgs e)
    {
        Cursor = _defaultCursor;
        GroupProgram_MouseLeave(sender, e);
    }


    private void GroupProgram_MouseEnter(object sender, EventArgs e)
    {
        _borderColor = _hoverBorderColor;
        groupProgram.Invalidate(); // Force redraw
    }

    private void GroupProgram_MouseLeave(object sender, EventArgs e)
    {
        _borderColor = DefaultGroupBorderColor;
        groupProgram.Invalidate(); // Force redraw
    }

    private void labelProgram_Click(object sender, EventArgs e)
    {
        OnProgramCardClicked(e);
    }

    private void GroupProgram_CustomButtonClick(object sender, DevExpress.XtraBars.Docking2010.BaseButtonEventArgs e)
    {
        if (string.CompareOrdinal(e.Button.Properties.Tag.ToString(), "Run") == 0)
        {
            OnProgramCardClicked(e);
        }


    }

    private void lblImage_Click(object sender, EventArgs e)
    {
        OnProgramCardClicked(e);
    }

    public SvgImage SvgImage
    {
        get => lblImage.ImageOptions.SvgImage;
        set
        {
            lblImage.ImageOptions.SvgImage = value;
            lblImage.ImageOptions.SvgImageSize = new Size(48, 48); // Set the desired width and height here
        }
    }

    // Add the description property
    public string Description
    {
        get => labelProgram.Text;
        set => labelProgram.Text = value;
    }

    public string Caption
    {
        get => groupProgram.Text;
        set => groupProgram.Text = value;
    }

    public string OffText
    {
        get => toggleShortcut.Properties.OffText;
        set => toggleShortcut.Properties.OffText = value;
    }

    public string OnText
    {
        get => toggleShortcut.Properties.OnText;
        set => toggleShortcut.Properties.OnText = value;
    }


    /// <summary>
    /// Gets or sets the color of the border when the mouse hovers over the control.
    /// </summary>
    /// <exception cref="ArgumentException">Thrown when the specified color is not found in the PredefinedColors enum.</exception>
    public Color HoverBorderColor
    {
        get => _hoverBorderColor;
        set
        {
            _hoverBorderColor = value;

        }
    }

    /// <summary>
    /// Gets the default group border color.
    /// </summary>
    private Color DefaultGroupBorderColor
    {
        get
        {
            var activeSkin = CommonSkins.GetSkin(LookAndFeel.ActiveLookAndFeel);
            var gpSkin = activeSkin[CommonSkins.SkinGroupPanel];
            var borderColor = gpSkin.Border.All;
            return borderColor;
        }
    }
}