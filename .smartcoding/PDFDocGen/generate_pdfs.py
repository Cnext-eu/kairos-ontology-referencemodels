#!/usr/bin/env python3
"""
PDF Generator for HLSD Documentation using xhtml2pdf
Converts markdown files with PlantUML diagrams into formatted PDFs.
"""

import os
import re
import sys
import requests
import base64
from datetime import datetime
from pathlib import Path

import markdown
from xhtml2pdf import pisa


class PDFGenerator:
    """Generate styled PDFs from markdown files using xhtml2pdf."""
    
    def __init__(self, project_name="project", output_dir=None):
        self.project_name = project_name
        self.project_title = project_name  # Use project name as-is
        
        if output_dir is None:
            # Find latest version folder in .docs/1-HLSD and create pdf-output subfolder
            # Path structure: .smartcoding/PDFDocGen/generate_pdfs.py -> parent is PDFDocGen, parent.parent is .smartcoding, parent.parent.parent is repo root
            hlsd_dir = Path(__file__).parent.parent.parent / ".docs" / "1-HLSD"
            version_folders = [f for f in hlsd_dir.glob("version*") if f.is_dir()]
            if not version_folders:
                raise FileNotFoundError(f"No version folders found in {hlsd_dir}")
            # Sort by folder name (which contains timestamp) to get latest
            latest_version = sorted(version_folders, key=lambda x: x.name)[-1]
            base_dir = latest_version / "pdf-output"
            self.output_dir = base_dir
            self.screen_output_dir = latest_version / "screen-diagrams"
        else:
            self.output_dir = Path(output_dir)
            self.screen_output_dir = Path(output_dir).parent / "screen-diagrams"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.screen_output_dir.mkdir(parents=True, exist_ok=True)
        
        # CSS styling for professional document layout
        self.css = """
        @page {
            size: a4 portrait;
            margin: 2.5cm 2cm 2.5cm 2cm;
            
            @frame footer {
                -pdf-frame-content: footerContent;
                bottom: 0.5cm;
                margin-left: 2cm;
                margin-right: 2cm;
                height: 1.5cm;
            }
        }
        
        body {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 10pt;
            line-height: 1.6;
            color: #333;
        }
        
        .page-header {
            width: 100%;
            border-bottom: 0.5pt solid #1a1a1a;
            margin-bottom: 15pt;
            padding-bottom: 5pt;
        }
        
        .page-header table {
            width: 100%;
            border: none;
            margin: 0;
            padding: 0;
        }
        
        .page-header td {
            border: none;
            padding: 0;
            vertical-align: middle;
        }
        
        .page-header .header-text {
            font-size: 10pt;
            font-weight: bold;
            color: #1a1a1a;
        }
        
        .page-header .header-logo {
            text-align: right;
        }
        
        .page-header .header-logo img {
            height: 20pt;
            vertical-align: middle;
        }
        
        h1 {
            font-size: 24pt;
            color: #1a1a1a;
            margin-top: 20pt;
            margin-bottom: 12pt;
            page-break-before: always;
            page-break-after: avoid;
            font-weight: bold;
        }
        
        h1.no-break {
            page-break-before: auto;
        }
        
        h2 {
            font-size: 18pt;
            color: #2a2a2a;
            margin-top: 16pt;
            margin-bottom: 10pt;
            page-break-before: always;
            page-break-after: avoid;
            font-weight: bold;
            border-bottom: 2px solid #2a5599;
            padding-bottom: 4pt;
        }
        
        h2.no-break {
            page-break-before: auto;
        }
        
        h3 {
            font-size: 14pt;
            color: #3a3a3a;
            margin-top: 12pt;
            margin-bottom: 8pt;
            page-break-after: avoid;
            font-weight: bold;
        }
        
        h4 {
            font-size: 12pt;
            color: #4a4a4a;
            margin-top: 10pt;
            margin-bottom: 6pt;
            page-break-after: avoid;
            font-weight: bold;
        }
        
        h5, h6 {
            font-size: 11pt;
            color: #5a5a5a;
            margin-top: 8pt;
            margin-bottom: 6pt;
            page-break-after: avoid;
            font-weight: bold;
        }
        
        p {
            margin-top: 0;
            margin-bottom: 8pt;
        }
        
        ul, ol {
            margin-top: 4pt;
            margin-bottom: 8pt;
            padding-left: 25pt;
        }
        
        li {
            margin-bottom: 4pt;
        }
        
        ul li {
            list-style-type: disc;
        }
        
        ul ul li {
            list-style-type: circle;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 8pt;
            margin-bottom: 12pt;
            page-break-inside: avoid;
        }
        
        thead {
            display: table-header-group;
        }
        
        th {
            background-color: #2a5599;
            color: white;
            font-weight: bold;
            padding: 8pt 6pt;
            text-align: left;
            border: 1pt solid #2a5599;
            font-size: 10pt;
        }
        
        td {
            padding: 6pt;
            border: 0.5pt solid #ccc;
            vertical-align: top;
            font-size: 9pt;
        }
        
        tbody tr:nth-child(even) {
            background-color: #f5f5f5;
        }
        
        tbody tr:nth-child(odd) {
            background-color: white;
        }
        
        code {
            font-family: "Courier New", Courier, monospace;
            background-color: #f4f4f4;
            padding: 2pt 4pt;
            font-size: 9pt;
        }
        
        pre {
            font-family: "Courier New", Courier, monospace;
            background-color: #f4f4f4;
            padding: 8pt;
            border-left: 4pt solid #2a5599;
            overflow-x: auto;
            margin: 8pt 0;
            font-size: 8pt;
            line-height: 1.4;
        }
        
        pre code {
            background-color: transparent;
            padding: 0;
        }
        
        blockquote {
            border-left: 4pt solid #ccc;
            margin-left: 0;
            padding-left: 12pt;
            color: #666;
            font-style: italic;
        }
        
        hr {
            border: none;
            border-top: 1pt solid #ccc;
            margin: 16pt 0;
        }
        
        img {
            max-width: 90%;
            height: auto;
            display: block;
            margin: 12pt auto;
        }
        
        .diagram {
            text-align: center;
            margin: 16pt 0;
            page-break-inside: avoid;
        }
        
        .diagram img {
            max-width: 100%;
            height: auto;
            border: 1px solid #e0e0e0;
            border-radius: 4pt;
            padding: 8pt;
            background-color: #fafafa;
        }
        
        .diagram-placeholder {
            border: 1px dashed #ccc;
            padding: 20pt;
            text-align: center;
            color: #666;
            font-style: italic;
            margin: 16pt 0;
        }
        
        a {
            color: #2a5599;
            text-decoration: none;
        }
        
        .title-page {
            text-align: center;
            padding-top: 30%;
        }
        
        .title-page h1 {
            font-size: 28pt;
            margin-bottom: 12pt;
            border-bottom: none;
        }
        
        .title-page h2 {
            font-size: 20pt;
            border-bottom: none;
            margin-bottom: 24pt;
        }
        
        .title-page p {
            font-size: 12pt;
            color: #666;
            margin: 8pt 0;
        }
        
        .page-break {
            page-break-after: always;
        }
        
        .header {
            font-size: 10pt;
            font-weight: bold;
            color: #1a1a1a;
            border-bottom: 0.5pt solid #1a1a1a;
            padding-bottom: 4pt;
        }
        
        .header-logo {
            height: 18pt;
            float: right;
            margin-left: 10pt;
        }
        
        .footer {
            font-size: 7pt;
            color: #666;
            border-top: 0.5pt solid #999;
            padding-top: 4pt;
        }
        
        .footer table {
            width: 100%;
            border: none;
            margin: 0;
            padding: 0;
        }
        
        .footer td {
            border: none;
            padding: 0;
            vertical-align: middle;
        }
        
        .footer-left {
            text-align: left;
            font-size: 7pt;
            color: #666;
        }
        
        .footer-center {
            text-align: center;
            font-size: 7pt;
            color: #666;
        }
        
        .footer-right {
            text-align: right;
            font-size: 7pt;
            color: #666;
        }
        """
    
    def generate_plantuml_image(self, plantuml_code, diagram_name):
        """Generate PNG image from PlantUML code using PlantUML server."""
        try:
            compressed = self._encode_plantuml(plantuml_code)
            url = f"http://www.plantuml.com/plantuml/png/{compressed}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            png_path = self.output_dir / f"{diagram_name}.png"
            png_path.write_bytes(response.content)
            
            return str(png_path)
            
        except Exception as e:
            print(f"Warning: Could not generate PlantUML diagram '{diagram_name}': {e}")
            return None
    
    def generate_mermaid_image(self, mermaid_code, diagram_name):
        """Generate PNG image from Mermaid code using mermaid.ink service.
        
        Optimized for PDF/Word page embedding with:
        - Higher scale (2x) for print quality
        - White background for clean print
        - Default theme (neutral colors, good for print)
        - Wider layout for A4/Letter page fit
        - C4 diagrams optimized for horizontal layout
        """
        try:
            import json
            
            # Detect diagram type for specific optimizations
            is_c4 = 'C4Context' in mermaid_code or 'C4Container' in mermaid_code or 'C4Component' in mermaid_code
            is_sequence = 'sequenceDiagram' in mermaid_code
            is_gantt = 'gantt' in mermaid_code
            
            optimized_code = mermaid_code
            
            # For C4 diagrams, just update the layout config (init directive breaks C4)
            if is_c4:
                # Increase shapes per row for more horizontal layout
                optimized_code = re.sub(
                    r'UpdateLayoutConfig\(\$c4ShapeInRow="[0-9]+",\s*\$c4BoundaryInRow="[0-9]+"\)',
                    'UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="2")',
                    optimized_code
                )
                if 'UpdateLayoutConfig' not in optimized_code:
                    optimized_code = optimized_code.rstrip() + '\n    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="2")'
                final_code = optimized_code
            else:
                # Non-C4 diagrams: apply init config
                mermaid_config = {
                    "theme": "default",
                    "themeVariables": {
                        "fontSize": "14px",
                        "fontFamily": "Arial, sans-serif"
                    }
                }
                
                if is_sequence:
                    mermaid_config["sequence"] = {
                        "diagramMarginX": 50,
                        "diagramMarginY": 10,
                        "actorMargin": 50,
                        "width": 150,
                        "height": 65,
                        "boxMargin": 10,
                        "boxTextMargin": 5,
                        "noteMargin": 10,
                        "messageMargin": 35
                    }
                else:
                    mermaid_config["flowchart"] = {
                        "htmlLabels": True,
                        "curve": "basis",
                        "nodeSpacing": 50,
                        "rankSpacing": 50,
                        "padding": 15
                    }
                
                config_json = json.dumps(mermaid_config)
                final_code = f"%%{{init: {config_json}}}%%\n{optimized_code}"
            
            # Encode the mermaid code to base64
            mermaid_bytes = final_code.encode('utf-8')
            mermaid_b64 = base64.urlsafe_b64encode(mermaid_bytes).decode('utf-8')
            
            # Use wider width for C4 diagrams
            width = 1000 if is_c4 else 800
            
            url = f"https://mermaid.ink/img/{mermaid_b64}?type=png&bgColor=white&scale=2&width={width}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=60, headers=headers)
            response.raise_for_status()
            
            png_path = self.output_dir / f"{diagram_name}.png"
            png_path.write_bytes(response.content)
            
            print(f"    [+] Rendered Mermaid diagram (print): {diagram_name}")
            return str(png_path)
            
        except Exception as e:
            print(f"    [-] Warning: Could not generate Mermaid diagram '{diagram_name}': {e}")
            return None
    
    def generate_mermaid_image_screen(self, mermaid_code, diagram_name):
        """Generate PNG image from Mermaid code optimized for screen viewing.
        
        Optimized for screen/presentation with:
        - Horizontal (LR) layout where applicable for better overview
        - Wider canvas for screen display
        - Forest theme for better screen contrast
        - Larger spacing for clarity
        - C4 diagrams with maximum horizontal spread
        """
        try:
            import json
            
            # Detect diagram type
            is_c4 = 'C4Context' in mermaid_code or 'C4Container' in mermaid_code or 'C4Component' in mermaid_code
            is_sequence = 'sequenceDiagram' in mermaid_code
            is_gantt = 'gantt' in mermaid_code
            
            screen_code = mermaid_code
            
            # Convert flowchart TB to LR for horizontal layout
            screen_code = re.sub(r'flowchart\s+TB', 'flowchart LR', screen_code)
            screen_code = re.sub(r'flowchart\s+TD', 'flowchart LR', screen_code)
            screen_code = re.sub(r'graph\s+TB', 'graph LR', screen_code)
            screen_code = re.sub(r'graph\s+TD', 'graph LR', screen_code)
            
            # For C4 diagrams, just update the layout config (init directive breaks C4)
            if is_c4:
                screen_code = re.sub(
                    r'UpdateLayoutConfig\(\$c4ShapeInRow="[0-9]+",\s*\$c4BoundaryInRow="[0-9]+"\)',
                    'UpdateLayoutConfig($c4ShapeInRow="5", $c4BoundaryInRow="3")',
                    screen_code
                )
                if 'UpdateLayoutConfig' not in screen_code:
                    screen_code = screen_code.rstrip() + '\n    UpdateLayoutConfig($c4ShapeInRow="5", $c4BoundaryInRow="3")'
                final_code = screen_code
            else:
                # Non-C4 diagrams: apply init config with forest theme
                mermaid_config = {
                    "theme": "forest",
                    "themeVariables": {
                        "fontSize": "16px",
                        "fontFamily": "Arial, sans-serif"
                    }
                }
                
                if is_sequence:
                    mermaid_config["sequence"] = {
                        "diagramMarginX": 80,
                        "diagramMarginY": 20,
                        "actorMargin": 80,
                        "width": 180,
                        "height": 70,
                        "boxMargin": 15,
                        "boxTextMargin": 8,
                        "noteMargin": 15,
                        "messageMargin": 50,
                        "mirrorActors": True
                    }
                else:
                    mermaid_config["flowchart"] = {
                        "htmlLabels": True,
                        "curve": "basis",
                        "nodeSpacing": 80,
                        "rankSpacing": 80,
                        "padding": 20,
                        "useMaxWidth": False
                    }
                
                config_json = json.dumps(mermaid_config)
                final_code = f"%%{{init: {config_json}}}%%\n{screen_code}"
            
            # Encode the mermaid code to base64
            mermaid_bytes = final_code.encode('utf-8')
            mermaid_b64 = base64.urlsafe_b64encode(mermaid_bytes).decode('utf-8')
            
            # Use wider width for C4 and screen viewing
            width = 1600 if is_c4 else 1200
            
            url = f"https://mermaid.ink/img/{mermaid_b64}?type=png&bgColor=!f8f9fa&scale=2&width={width}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=60, headers=headers)
            response.raise_for_status()
            
            png_path = self.screen_output_dir / f"{diagram_name}-screen.png"
            png_path.write_bytes(response.content)
            
            print(f"    [+] Rendered Mermaid diagram (screen): {diagram_name}-screen")
            return str(png_path)
            
        except Exception as e:
            print(f"    [-] Warning: Could not generate screen Mermaid diagram '{diagram_name}': {e}")
            return None
    
    def _encode_plantuml(self, plantuml_text):
        """Encode PlantUML text for use in URL."""
        import zlib
        
        plantuml_alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
        compressed = zlib.compress(plantuml_text.encode('utf-8'))[2:-4]
        
        encoded = ''
        for i in range(0, len(compressed), 3):
            if i + 2 < len(compressed):
                b1, b2, b3 = compressed[i], compressed[i + 1], compressed[i + 2]
                encoded += plantuml_alphabet[(b1 >> 2) & 0x3F]
                encoded += plantuml_alphabet[((b1 & 0x3) << 4) | ((b2 >> 4) & 0xF)]
                encoded += plantuml_alphabet[((b2 & 0xF) << 2) | ((b3 >> 6) & 0x3)]
                encoded += plantuml_alphabet[b3 & 0x3F]
            elif i + 1 < len(compressed):
                b1, b2 = compressed[i], compressed[i + 1]
                encoded += plantuml_alphabet[(b1 >> 2) & 0x3F]
                encoded += plantuml_alphabet[((b1 & 0x3) << 4) | ((b2 >> 4) & 0xF)]
                encoded += plantuml_alphabet[(b2 & 0xF) << 2]
            else:
                b1 = compressed[i]
                encoded += plantuml_alphabet[(b1 >> 2) & 0x3F]
                encoded += plantuml_alphabet[(b1 & 0x3) << 4]
        
        return encoded
    
    def get_logo_base64(self):
        """Get Cnext logo as base64 string."""
        logo_path = Path(__file__).parent / "cnext-logo.png"
        
        if logo_path.exists():
            print(f"  [+] Loading logo from: {logo_path}")
            with open(logo_path, 'rb') as f:
                logo_data = base64.b64encode(f.read()).decode('utf-8')
                print(f"  [+] Logo encoded: {len(logo_data)} characters")
                return logo_data
        else:
            print(f"  [-] Logo not found at: {logo_path}")
        
        # Return 1x1 transparent PNG as fallback
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    def preprocess_markdown(self, content, filename):
        """Extract Mermaid and PlantUML diagrams and replace with image references.
        Also replace emoji characters with text equivalents for PDF compatibility.
        """
        # Replace emoji with text equivalents
        emoji_map = {
            '\u2705': '[v]',  # ✅
            '\u274c': '[x]',  # ❌
            '\u26a0\ufe0f': '[!]',  # ⚠️
            '\u26a0': '[!]',  # ⚠
            '\u2139\ufe0f': '[i]',  # ℹ️
            '\u2139': '[i]',  # ℹ
        }
        for emoji, replacement in emoji_map.items():
            content = content.replace(emoji, replacement)
        
        diagram_count = 0
        base_name = Path(filename).stem
        
        def replace_mermaid(match):
            nonlocal diagram_count
            diagram_count += 1
            code = match.group(1).strip()
            diagram_name = f"{base_name}-mermaid-{diagram_count}"
            
            # Generate print-optimized version (for PDF embedding)
            img_path = self.generate_mermaid_image(code, diagram_name)
            
            # Also generate screen-optimized version (horizontal layout)
            self.generate_mermaid_image_screen(code, diagram_name)
            
            if img_path:
                # Embed print version image as base64 in PDF
                with open(img_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                return f'\n<div class="diagram"><img src="data:image/png;base64,{img_data}" alt="Mermaid Diagram" style="max-width: 100%; height: auto; display: block; margin: 10pt auto;"/></div>\n'
            # If rendering failed, show placeholder
            return f'\n<div class="diagram-placeholder" style="border: 1px dashed #ccc; padding: 10pt; text-align: center; color: #666;">[Diagram: {diagram_name}]</div>\n'
        
        def replace_plantuml(match):
            nonlocal diagram_count
            diagram_count += 1
            code = match.group(1)
            diagram_name = f"{base_name}-plantuml-{diagram_count}"
            img_path = self.generate_plantuml_image(code, diagram_name)
            
            if img_path:
                # Embed image as base64
                with open(img_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                return f'\n<div class="diagram"><img src="data:image/png;base64,{img_data}" alt="PlantUML Diagram" style="max-width: 100%; height: auto; display: block; margin: 10pt auto;"/></div>\n'
            return match.group(0)
        
        # Process Mermaid diagrams first
        content = re.sub(r'```mermaid\s*\n(.*?)\n```', replace_mermaid, content, flags=re.DOTALL)
        
        # Then process PlantUML diagrams
        content = re.sub(r'```plantuml\s*\n(.*?)\n```', replace_plantuml, content, flags=re.DOTALL)
        
        return content, diagram_count
    
    def generate_pdf(self, markdown_file, output_file=None):
        """Generate PDF from a markdown file."""
        markdown_path = Path(markdown_file)
        
        if not markdown_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {markdown_file}")
        
        print(f"Processing: {markdown_path.name}")
        markdown_content = markdown_path.read_text(encoding='utf-8')
        
        # Preprocess and extract PlantUML diagrams
        markdown_content, diagram_count = self.preprocess_markdown(markdown_content, markdown_path.name)
        
        if output_file is None:
            output_file = self.output_dir / f"{markdown_path.stem}.pdf"
        else:
            output_file = Path(output_file)
        
        print(f"Generating PDF: {output_file.name}")
        
        # Document titles
        doc_titles = {
            '01-executive-summary.md': 'Executive Summary',
            '02-c4-context.md': 'C4 Context Diagram',
            '03-c4-container.md': 'C4 Container Diagram',
            '04-c4-component.md': 'C4 Component Diagram',
            '05-key-flows.md': 'Key Processing Flows',
            '06-security-compliance.md': 'Security & Compliance',
            '07-operational-model.md': 'Operational Model',
            '08-delivery-plan.md': 'Delivery Plan',
            '09-risks-open-questions.md': 'Risks & Open Questions',
            'README.md': 'Overview'
        }
        
        title = doc_titles.get(markdown_path.name, 'Documentation')
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=[
            'extra', 'nl2br', 'sane_lists', 'toc', 'codehilite', 'attr_list',
        ])
        
        content_html = md.convert(markdown_content)
        
        # Add no-break class to first h1 and h2
        content_html = content_html.replace('<h1>', '<h1 class="no-break">', 1)
        content_html = content_html.replace('<h2>', '<h2 class="no-break">', 1)
        
        logo_data = self.get_logo_base64()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{self.project_title} - {title}</title>
            <style>
                {self.css}
            </style>
        </head>
        <body>
            <div class="page-header">
                <table>
                    <tr>
                        <td class="header-text">{self.project_title} - HLSD</td>
                        <td class="header-logo"><img src="data:image/png;base64,{logo_data}" alt="Cnext"/></td>
                    </tr>
                </table>
            </div>
            
            <div id="footerContent">
                <div class="footer">
                    <table>
                        <tr>
                            <td class="footer-left">{title}</td>
                            <td class="footer-center">&copy; {datetime.now().year} Cnext - All Rights Reserved</td>
                            <td class="footer-right">Page <pdf:pagenumber></td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div class="title-page">
                <h1 class="no-break">{self.project_title}</h1>
                <h2 class="no-break">{title}</h2>
                <p>Version 1.0</p>
                <p>{datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            <div class="page-break"></div>
            {content_html}
        </body>
        </html>
        """
        
        # Generate PDF
        with open(output_file, 'wb') as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file, encoding='utf-8')
        
        if pisa_status.err:
            raise Exception(f"Error generating PDF: {pisa_status.err} errors")
        
        if diagram_count > 0:
            print(f"  [+] Saved {diagram_count} diagram(s)")
        
        print(f"[+] Created: {output_file}")
        return output_file
    
    def generate_all(self, docs_dir="../docs"):
        """Generate PDFs for all markdown files."""
        docs_path = Path(docs_dir)
        
        if not docs_path.exists():
            raise FileNotFoundError(f"Documentation directory not found: {docs_dir}")
        
        markdown_files = sorted(docs_path.glob("*.md"))
        
        if not markdown_files:
            raise FileNotFoundError(f"No markdown files found in {docs_dir}")
        
        print(f"\n{'='*60}")
        print(f"PDF Generator for HLSD Documentation")
        print(f"{'='*60}\n")
        print(f"Found {len(markdown_files)} markdown file(s)")
        print(f"PDF output directory: {self.output_dir.absolute()}")
        print(f"Screen diagrams directory: {self.screen_output_dir.absolute()}\n")
        
        generated_pdfs = []
        
        for md_file in markdown_files:
            try:
                pdf_file = self.generate_pdf(md_file)
                generated_pdfs.append(pdf_file)
                print()
            except Exception as e:
                import traceback
                print(f"[X] Error processing {md_file.name}: {e}")
                traceback.print_exc()
                print()
        
        print(f"{'='*60}")
        print(f"[+] Generated {len(generated_pdfs)} PDF(s)")
        print(f"{'='*60}\n")
        
        return generated_pdfs


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate PDFs from HLSD markdown files')
    parser.add_argument('--project', type=str, default='project',
                        help='Project short name (e.g., kidslife, myproject)')
    args = parser.parse_args()
    
    generator = PDFGenerator(project_name=args.project)
    
    # Find latest version folder
    # Path structure: PDFDocGen/generate_pdfs.py -> parent is PDFDocGen, parent.parent is .smartcoding, parent.parent.parent is repo root
    script_dir = Path(__file__).parent
    hlsd_dir = script_dir.parent.parent / ".docs" / "1-HLSD"
    version_folders = [f for f in hlsd_dir.glob("version*") if f.is_dir()]
    if not version_folders:
        print(f"Error: No version folders found in {hlsd_dir}")
        sys.exit(1)
    latest_version = sorted(version_folders, key=lambda x: x.name)[-1]
    print(f"Found latest version: {latest_version.name}")
    docs_dir = latest_version
    
    try:
        generator.generate_all(docs_dir)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
