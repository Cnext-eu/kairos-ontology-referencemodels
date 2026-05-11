# AI Instructions for HLSD PDF Generation

## Context for AI Assistant

You are helping generate professional PDF documents from an existing High Level Solution Design (HLSD) using the automated PDF generation tool.

## Prerequisites

Before generating PDFs, ensure:
1. **HLSD exists** in `.docs/HLSD/version {timestamp}/` folder with all markdown files
2. **Python 3.8+** is installed and accessible
3. **Internet connection** is available (for PlantUML diagram rendering)

## Your Task

Guide the user through PDF generation using the provided PowerShell script.

---

## PDF Generation Process

### Automated Generation (Recommended)

The PDF generator automatically:
1. Finds the **latest HLSD version folder** in `.docs/HLSD/`
2. Creates a `pdf-output/` subfolder inside that version
3. Converts all markdown files to professionally styled PDFs
4. Renders PlantUML diagrams as embedded images
5. Applies Cnext branding and formatting

### Command

```powershell
# Navigate to tools directory
cd .docs/tools

# Generate all PDFs (default)
.\generate.ps1

# Or generate specific documents
.\generate.ps1 --file "01-executive-summary.md"

# Or generate all with verbose output
.\generate.ps1 --all --verbose
```

---

## Folder Structure

The tool expects this structure:

```
.docs/
├── 1-HLSD/
│   ├── feedback-log.md                  # Persistent feedback across versions
│   └── version-{YYYYMMDD}T{HHMMSS}/     # Latest version auto-detected
│       ├── README.md
│       ├── 01-executive-summary.md
│       ├── 02-c4-context.md
│       ├── 03-key-flows.md
│       ├── 04-security-compliance.md
│       ├── 05-operational-model.md
│       ├── 06-delivery-plan.md
│       ├── 07-risks-open-questions.md
│       ├── pdf-output/                  # Auto-created by tool
│       │   ├── 01-executive-summary.pdf
│       │   ├── 02-c4-context.pdf
│       │   └── ... (all generated PDFs)
│       └── screen-diagrams/             # Screen-optimized Mermaid exports
│           ├── c4-context-screen.png
│           └── ... (wider layout diagrams)
└── tools/
    ├── generate.ps1                     # PowerShell launcher
    ├── generate_pdfs.py                 # Python PDF generator
    ├── requirements.txt                 # Python dependencies
    ├── pdf_style.css                    # PDF styling
    └── cnext-logo.png                   # Company logo for branding
```

### Output Folders

| Folder | Purpose | Contents |
|--------|---------|----------|
| `pdf-output/` | Print-ready PDFs | Diagrams with `$c4ShapeInRow="3"` |
| `screen-diagrams/` | Web/screen viewing | Diagrams with `$c4ShapeInRow="4"` |

---

## What the Tool Does

### 1. Environment Setup
- Creates Python virtual environment (if needed)
- Installs dependencies: `markdown`, `xhtml2pdf`, `requests`

### 2. Markdown Processing
- Parses all `.md` files in the latest HLSD version folder
- Converts markdown to HTML with proper formatting
- Extracts PlantUML code blocks

### 3. Mermaid & PlantUML Diagram Rendering

**Mermaid Diagrams (Preferred):**
- Rendered directly using Mermaid CLI or browser-based rendering
- Supports C4, sequence, flowchart, Gantt, and ER diagrams
- Layout can be optimized for print vs. screen

**PlantUML Diagrams (Legacy):**
- Sends PlantUML code to public server: `https://www.plantuml.com/plantuml`
- Retrieves rendered PNG diagrams
- Embeds diagrams as base64 images in PDF

**Diagram Width Settings:**

| Diagram Type | Print Width | Screen Width |
|--------------|-------------|-------------|
| C4 Context | 100% page width | 1200px max |
| Sequence | 80% page width | 900px max |
| Flowchart | 90% page width | 1000px max |

### 4. PDF Generation
- Applies professional styling (headers, footers, page numbers)
- Adds Cnext logo to headers
- Creates table of contents (in README.md)
- Formats code blocks, tables, lists
- Handles page breaks intelligently

### 5. Output
- Saves PDFs to `{version folder}/pdf-output/`
- Opens output folder automatically
- Provides summary of generated files

---

## Command Line Options

### Generate All PDFs (Default)

```powershell
.\generate.ps1
# Or explicitly:
.\generate.ps1 --all
```

### Generate Specific File

```powershell
.\generate.ps1 --file "02-c4-context.md"
```

### Verbose Output

```powershell
.\generate.ps1 --all --verbose
```

### Help

```powershell
.\generate.ps1 --help
```

---

## Customization

### Logo Replacement

Replace `.docs/tools/cnext-logo.png` with your company logo:
- Recommended size: 200x60 pixels (transparent PNG)
- Will appear in PDF headers

### Styling

Edit `.docs/tools/pdf_style.css` to customize:
- Colors, fonts, spacing
- Header/footer format
- Page margins
- Table styling

### PlantUML Server

By default uses public server: `https://www.plantuml.com/plantuml`

To use a local server, edit `generate_pdfs.py`:
```python
PLANTUML_SERVER = "http://localhost:8080"
```

---

## Troubleshooting

### Python Not Found

**Error:** `Python not found. Please install Python 3.8 or later.`

**Solution:**
1. Install Python from: https://www.python.org/downloads/
2. Ensure Python is in PATH (check during installation)
3. Verify: `python --version`

### PlantUML Rendering Fails

**Error:** `Failed to render PlantUML diagram`

**Solution:**
1. Check internet connection
2. Verify PlantUML server is accessible: https://www.plantuml.com/plantuml
3. Check PlantUML syntax in markdown files

### Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'markdown'`

**Solution:**
```powershell
cd .docs/tools
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### No Version Folder Found

**Error:** `No version folders found in .docs/HLSD`

**Solution:**
1. Ensure HLSD has been generated first (see AI_INSTRUCTIONS-1-HLSD.md)
2. Check folder naming: `version {YYYYMMDD}T{HHMMSS}`

### Logo Not Displaying

**Issue:** PDF headers show no logo

**Solution:**
1. Ensure `cnext-logo.png` exists in `.docs/tools/`
2. Check file format: PNG recommended
3. Verify file permissions (readable)

---

## Expected Output

### Console Output

```
Kidslife IDP - PDF Generator
=============================

✓ Python found: Python 3.11.5
✓ Virtual environment created
✓ Dependencies installed

Generating PDFs...

Processing: README.md
  [+] Loading logo from: G:\Git\...\tools\cnext-logo.png
  [+] Logo encoded: 12345 characters
  [+] Rendered 0 PlantUML diagrams
  [✓] Generated: README.pdf

Processing: 01-executive-summary.md
  [+] Rendered 0 PlantUML diagrams
  [✓] Generated: 01-executive-summary.pdf

Processing: 02-c4-context.md
  [+] Found PlantUML diagram: System Context
  [+] Rendered 1 PlantUML diagrams
  [✓] Generated: 02-c4-context.pdf

... (more files)

=============================
✓ PDF generation complete!

Opening output directory: version 20251221T202157/pdf-output
```

### Output Files

All PDFs in: `.docs/HLSD/version {timestamp}/pdf-output/`
- `README.pdf`
- `01-executive-summary.pdf`
- `02-c4-context.pdf`
- `03-c4-container.pdf`
- `04-c4-component.pdf`
- `05-key-flows.pdf`
- `06-security-compliance.pdf`
- `07-operational-model.pdf`
- `08-delivery-plan.pdf`
- `09-risks-open-questions.pdf`

---

## PDF Features

### Professional Formatting
- **Headers:** Document title + Cnext logo
- **Footers:** Page numbers (e.g., "Page 3 of 15")
- **Table of Contents:** In README.pdf
- **Consistent Styling:** Headings, tables, code blocks

### PlantUML Diagrams
- High-quality PNG embedded in PDFs
- Scales to fit page width
- Preserves aspect ratio

### Code Blocks
- Syntax highlighting (basic)
- Monospace font
- Borders and background color

### Tables
- Striped rows (alternating colors)
- Header row with dark background
- Auto-sizing columns

---

## Workflow with AI Assistant

### Typical Conversation Flow

**User:** "Generate PDFs for my HLSD"

**You (AI Assistant):**
1. Verify HLSD exists: Check `.docs/HLSD/version {timestamp}/` has markdown files
2. Guide user to run command:
   ```powershell
   cd .docs/tools
   .\generate.ps1
   ```
3. Explain what will happen:
   - Tool finds latest HLSD version
   - Creates pdf-output subfolder
   - Converts all .md files to PDFs
   - Opens output folder when done

**User:** "PDF generation failed with error X"

**You (AI Assistant):**
1. Identify error category (Python, PlantUML, dependencies)
2. Provide troubleshooting steps from section above
3. If needed, check file contents for issues

**User:** "Can I customize the logo?"

**You (AI Assistant):**
- Explain logo replacement process
- Recommend dimensions and format
- Show file path: `.docs/tools/cnext-logo.png`

---

## Integration with HLSD Workflow

### Full Workflow

1. **Prepare Context** (Human)
   - Edit `.docs/tools/smartcoding/starter-requirements.md`

2. **Generate HLSD** (AI using AI_INSTRUCTIONS-1-HLSD.md)
   - Create versioned folder
   - Generate 10 markdown files with PlantUML diagrams

3. **Generate PDFs** (AI using AI_INSTRUCTIONS-3-HLSD-PDF.md) ← **You are here**
   - Run `.\generate.ps1`
   - Share PDFs with stakeholders

4. **Iterate** (Human + AI)
   - Review PDFs
   - Update requirements or HLSD
   - Regenerate (new version folder)

---

## Example AI Response

When user asks: **"Generate PDFs for the HLSD"**

```
I'll help you generate professional PDFs from your HLSD documentation.

First, let me verify the HLSD folder structure...
[Check if .docs/HLSD/version {timestamp}/ exists]

Great! I found the HLSD version folder. Now run this command:

```powershell
cd .docs/tools
.\generate.ps1
```

This will:
1. Set up Python environment (first time only)
2. Find your latest HLSD version
3. Convert all markdown files to PDFs
4. Render PlantUML diagrams
5. Save PDFs to: .docs/HLSD/version {timestamp}/pdf-output/

The tool will open the output folder when complete. 
PDFs will include Cnext branding, page numbers, and professionally formatted diagrams.

Let me know if you encounter any errors!
```

---

## Notes for AI Assistants

### Do:
- ✅ Check if HLSD exists before suggesting PDF generation
- ✅ Guide user step-by-step through command execution
- ✅ Explain what each step does (transparency)
- ✅ Offer troubleshooting if errors occur
- ✅ Mention customization options (logo, styling) if asked

### Don't:
- ❌ Run the PowerShell script yourself (user must run it)
- ❌ Edit PDF generator code unless user requests customization
- ❌ Assume Python is installed (check or ask user)
- ❌ Skip verification steps (always check folder structure)

---

## Summary

This tool automates HLSD PDF generation:
- **Input:** Markdown files in `.docs/HLSD/version {timestamp}/`
- **Output:** Professional PDFs in `{version folder}/pdf-output/`
- **Command:** `cd .docs/tools && .\generate.ps1`
- **Features:** PlantUML diagrams, Cnext branding, smart formatting

Your role as AI assistant: Guide user through the process, troubleshoot issues, and explain customization options.
