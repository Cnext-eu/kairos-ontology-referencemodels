# PDF Generator for IDP HLSD Documentation

This tool converts the markdown documentation files (01-09) into beautifully formatted PDF documents with embedded PlantUML diagrams.

## Features

✅ Professional formatting with custom styling  
✅ Automatic PlantUML diagram generation and embedding  
✅ Cnext branding (logo in header, copyright in footer)  
✅ Page headers with logo and footers with document info  
✅ Syntax-highlighted code blocks  
✅ Styled tables with blue headers and alternating rows  
✅ Page breaks on major headers (H1/H2)  
✅ Emoji text conversion for PDF compatibility  
✅ Timestamped output folders for version tracking  

## Quick Start

### Windows (PowerShell)

Simply double-click `generate.ps1` or run:

```powershell
.\generate.ps1
```

This will:
1. Create a virtual environment (first time only)
2. Install dependencies from requirements.txt
3. Prompt for project name
4. Generate PDFs for all documents
5. Open the output folder

### Manual Python Usage

#### 1. Install Dependencies

See `requirements.txt` for the list of required packages and installation instructions.

```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.8 or later
- See requirements.txt for package versions

#### 2. Generate PDFs

**Generate all documents:**
```bash
python generate_pdfs.py
```

The tool automatically processes all markdown files in the parent directory and generates individual PDFs.

## Output

PDFs are generated in the `pdf-output` folder within the latest HLSD version directory:

```
.docs/
└── 1-HLSD/
    └── version-20260201-143022/
        ├── pdf-output/
        │   ├── 01-executive-summary.pdf
        │   ├── 02-c4-context.pdf
        │   ├── 03-key-flows.pdf
        │   ├── 04-security-compliance.pdf
        │   ├── 05-operational-model.pdf
        │   ├── 06-delivery-plan.pdf
        │   ├── 07-risks-open-questions.pdf
        │   └── README.pdf
        └── screen-diagrams/         # Extracted diagrams as PNG files
            ├── 02-c4-context-diagram-1.png
            ├── 03-key-flows-diagram-1.png
            └── ...
```

**Tool Location:** `.smartcoding/PDFDocGen/` (part of SmartCoding AI instructions)

### PlantUML Diagrams

The tool automatically:
1. Extracts PlantUML code blocks from markdown
2. Generates PNG diagrams via PlantUML server API
3. Embeds diagrams as base64-encoded images in PDFs
4. Saves individual PNG files with meaningful names

## Styling

The PDF styling is controlled by inline CSS in `generate_pdfs.py`. Key features:

- **Colors**: Blue theme (#2a5599) for headers and table headers
- **Fonts**: Arial for body text, Courier New for code
- **Page Layout**: A4 portrait with 2.5cm margins
- **Tables**: Blue headers with white text, alternating row colors (#f5f5f5)
- **Code Blocks**: Gray background with blue left border
- **Page Breaks**: Automatic breaks before H1 and H2 headers (except first ones)

## Features & Formatting

### Page Header (Top)
- **Left**: "Kidslife IDP - HLSD"
- **Right**: Cnext logo (cnext-logo.png)
- Bordered bottom line

### Page Footer (Bottom)
- **Left**: Document name (e.g., "Executive Summary")
- **Center**: "© 2025 Cnext - All Rights Reserved"
- **Right**: Page number
- Bordered top line

### Title Page
Each PDF starts with a title page containing:
- Main title: "Kidslife Intelligent Document Processing"
- Document-specific subtitle
- Version number
- Generation date

### Content Formatting
- **Headings**: 
  - H1: 24pt, page break before (except first)
  - H2: 18pt with blue bottom border, page break before (except first)
  - H3-H6: Progressively smaller with proper spacing
- **Tables**: 
  - Blue headers (#2a5599) with white text
  - Alternating row colors for readability
  - Full-width with border collapse
- **Code Blocks**: 
  - Gray background (#f4f4f4)
  - Blue left border (4pt #2a5599)
  - Courier New font, syntax preserved
- **Lists**: 
  - Proper indentation (25pt)
  - Nested list support
  - Consistent spacing
- **Images/Diagrams**: 
  - Base64 embedded for reliability
  - Auto-sized to 90% max width
  - Centered alignment
- **Emoji Conversion**:
  - ✅ → [v]
  - ❌ → [x]
  - ⚠️ → [!]

### PlantUML Diagrams
PlantUML code blocks are automatically:
1. Detected via ```plantuml syntax
2. Sent to PlantUML server API for rendering
3. Embedded as base64-encoded PNG images
4. Saved as individual PNG files with descriptive names (e.g., "02-c4-context-diagram-1.png")

## Troubleshooting

### xhtml2pdf vs WeasyPrint

This tool uses **xhtml2pdf** (not WeasyPrint) because:
- ✅ Pure Python - no external dependencies
- ✅ Works on Windows without GTK installation
- ✅ Simpler installation and deployment
- ✅ Adequate for our documentation needs

### PlantUML Diagrams Not Generating

If diagrams fail to generate:

1. **Check internet connection** - requires access to http://www.plantuml.com/plantuml/png/
2. **Verify PlantUML syntax** - test your diagrams at https://www.plantuml.com/plantuml/uml/
3. **Check timeout** - large diagrams may need longer timeout (default: 30s)

### Logo Not Appearing

Ensure `cnext-logo.png` exists in the `tools` folder. The generator will use a 1x1 transparent placeholder if missing.

### Emoji Display Issues

Emojis are automatically converted to text equivalents:
- If you see raw unicode in the PDF, the conversion worked correctly
- Add more emoji mappings in the `preprocess_markdown()` method if needed

### Font Issues

The tool uses standard system fonts (Arial, Courier New) which should be available on all systems. No custom font installation required.

## Customization

### Change Colors

Edit the CSS string in `generate_pdfs.py`:

```python
# Find this section in the __init__ method
self.css = """
    ...
    h2 {
        border-bottom: 2px solid #2a5599;  # Change this color
    }
    
    th {
        background-color: #2a5599;  # Change this color
    }
    ...
"""
```

### Adjust Logo Size

Modify the `.page-header .header-logo img` CSS:

```python
.page-header .header-logo img {
    height: 20pt;  # Adjust size (current: 20pt)
}
```

### Add More Emoji Conversions

Edit the `preprocess_markdown()` method:

```python
emoji_map = {
    '\u2705': '[v]',  # ✅
    '\u274c': '[x]',  # ❌
    '\u26a0\ufe0f': '[!]',  # ⚠️
    '\u26a0': '[!]',  # ⚠
    # Add your emoji here:
    '\uYOUR_CODE': '[YOUR_TEXT]',
}
```

### Custom Document Titles

Edit the `doc_titles` dictionary in the `generate_pdf()` method:

```python
doc_titles = {
    '01-executive-summary.md': 'Your Custom Title',
    '02-c4-context.md': 'Your Custom Title',
    # ... add more
}
```

### Change Output Directory

Modify the `__init__` method to change the base output location:

```python
def __init__(self, output_dir=None):
    if output_dir is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_dir = Path(__file__).parent.parent / "pdf-output" / timestamp
        # Change "pdf-output" to your preferred folder name
```

## Technical Details

### Architecture

The tool uses:
- **xhtml2pdf (pisa)**: Pure Python PDF library
- **markdown**: Advanced markdown parser with extensions
- **PlantUML Server API**: http://www.plantuml.com/plantuml/png/
- **Base64 encoding**: For reliable image embedding
- **Pillow**: For logo file handling

### Markdown Extensions

Enabled extensions:
- `extra`: Tables, fenced code blocks, attributes
- `nl2br`: Newline to `<br>` conversion
- `sane_lists`: Better list handling
- `toc`: Table of contents support
- `codehilite`: Code syntax highlighting
- `attr_list`: Attribute lists for elements

### PlantUML Encoding

Diagrams are compressed and encoded using PlantUML's custom Base64 variant for URL transmission.

### File Structure

```
tools/
├── generate_pdfs.py         # Main generator script
├── generate.ps1              # PowerShell launcher
├── requirements.txt          # Python dependencies
├── cnext-logo.png           # Cnext logo
└── README.md                 # This file
```

## Support

For issues or questions:
- Review this README for common solutions
- Check xhtml2pdf documentation: https://xhtml2pdf.readthedocs.io/
- Check PlantUML documentation: https://plantuml.com/
- Contact Cnext support team

## Version History

- **v2.0** (2025-12-20): 
  - Migrated to xhtml2pdf for better Windows compatibility
  - Added PlantUML diagram generation and embedding
  - Added Cnext branding (logo and copyright)
  - Implemented three-column footer layout
  - Added emoji text conversion
  - Timestamped output folders
  
- **v1.0** (Initial): Basic PDF generation with ReportLab

## License

Part of the Kidslife IDP project documentation toolkit.  
© 2025 Cnext - All Rights Reserved
