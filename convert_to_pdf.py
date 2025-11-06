#!/usr/bin/env python3
"""
Convert Brewery Management System Technical Specification from Markdown to PDF
Professional formatting with cover page and proper styling
"""

import re
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Preformatted
)
from reportlab.lib.colors import HexColor

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, "TECHNICAL_SPECIFICATION.md")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "TECHNICAL_SPECIFICATION.pdf")

def setup_styles():
    """Create custom styles for the document"""
    styles = getSampleStyleSheet()
    
    # Cover page title
    styles.add(ParagraphStyle(
        name='CoverTitle',
        parent=styles['Title'],
        fontSize=32,
        textColor=HexColor('#1a365d'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Cover page subtitle
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=HexColor('#2c5282'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Custom heading styles
    styles.add(ParagraphStyle(
        name='CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#1a365d'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        keepWithNext=True
    ))
    
    styles.add(ParagraphStyle(
        name='CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#2c5282'),
        spaceAfter=10,
        spaceBefore=16,
        fontName='Helvetica-Bold',
        keepWithNext=True
    ))
    
    styles.add(ParagraphStyle(
        name='CustomH3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=HexColor('#2d3748'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        keepWithNext=True
    ))
    
    # Body text
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=HexColor('#2d3748'),
        alignment=TA_JUSTIFY,
        spaceAfter=8
    ))
    
    # Bullet list
    styles.add(ParagraphStyle(
        name='CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=HexColor('#2d3748'),
        leftIndent=20,
        bulletIndent=10,
        spaceAfter=6
    ))
    
    # Code/Preformatted
    styles.add(ParagraphStyle(
        name='CustomCode',
        parent=styles['Code'],
        fontSize=9,
        leading=11,
        textColor=HexColor('#1a202c'),
        backColor=HexColor('#f7fafc'),
        leftIndent=20,
        rightIndent=20,
        spaceAfter=10,
        spaceBefore=10
    ))
    
    return styles

def create_cover_page(styles):
    """Create a professional cover page"""
    story = []
    
    # Add top spacing
    story.append(Spacer(1, 2*inch))
    
    # Main title
    title = Paragraph("BREWERY MANAGEMENT SYSTEM", styles['CoverTitle'])
    story.append(title)
    
    # Subtitle
    subtitle = Paragraph("Complete Technical Specification", styles['CoverSubtitle'])
    story.append(subtitle)
    story.append(Spacer(1, 0.5*inch))
    
    # Version info
    version_info = [
        "Version: 1.0",
        "Date: November 5, 2025",
        "Status: Pre-Development - Ready to Build"
    ]
    
    for info in version_info:
        p = Paragraph(info, styles['CoverSubtitle'])
        story.append(p)
        story.append(Spacer(1, 0.2*inch))
    
    story.append(Spacer(1, 1*inch))
    
    # Project summary
    summary = Paragraph(
        "A comprehensive Windows desktop application for commercial brewery operations "
        "with Google Sheets cloud synchronization, offline capability, and HMRC-compliant "
        "UK alcohol duty calculations.",
        styles['CustomBody']
    )
    story.append(summary)
    
    story.append(PageBreak())
    return story

def clean_markdown_formatting(text):
    """Clean and convert markdown formatting to HTML for ReportLab"""
    # Escape special characters first
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    # Handle bold text - replace ** pairs with <b> tags
    # Use regex to properly match pairs
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
    
    # Handle inline code - backticks
    text = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', text)
    
    return text

def parse_markdown_line(line, styles, in_code_block, in_table):
    """Parse a single line of markdown and return formatted elements"""
    elements = []
    
    # Check for code blocks
    if line.strip().startswith('```'):
        return elements, not in_code_block, in_table
    
    if in_code_block:
        # Handle code blocks as plain text
        safe_line = line.rstrip().replace('<', '&lt;').replace('>', '&gt;')
        elements.append(Preformatted(safe_line, styles['CustomCode']))
        return elements, in_code_block, in_table
    
    # Skip empty lines
    if not line.strip():
        elements.append(Spacer(1, 0.1*inch))
        return elements, in_code_block, in_table
    
    try:
        # Headers
        if line.startswith('# ') and not line.startswith('##'):
            text = clean_markdown_formatting(line[2:].strip())
            elements.append(Paragraph(text, styles['CustomH1']))
        elif line.startswith('## ') and not line.startswith('###'):
            text = clean_markdown_formatting(line[3:].strip())
            elements.append(Paragraph(text, styles['CustomH2']))
        elif line.startswith('### '):
            text = clean_markdown_formatting(line[4:].strip())
            elements.append(Paragraph(text, styles['CustomH3']))
        
        # Horizontal rules
        elif line.strip().startswith('---'):
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph('_' * 80, styles['CustomBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Lists
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            text = clean_markdown_formatting(line.strip()[2:].strip())
            elements.append(Paragraph(f'• {text}', styles['CustomBullet']))
        
        # Numbered lists
        elif re.match(r'^\d+\.', line.strip()):
            text = re.sub(r'^\d+\.\s*', '', line.strip())
            text = clean_markdown_formatting(text)
            elements.append(Paragraph(text, styles['CustomBullet']))
        
        # Tables (simple handling - skip separators)
        elif '|' in line:
            if not line.strip().replace('-', '').replace('|', '').strip():
                # Skip table separator lines
                pass
            else:
                cells = [cell.strip() for cell in line.split('|')]
                cells = [c for c in cells if c]  # Remove empty
                if cells:
                    table_text = ' | '.join(cells)
                    table_text = clean_markdown_formatting(table_text)
                    elements.append(Paragraph(table_text, styles['CustomBody']))
        
        # Regular paragraphs
        elif line.strip():
            text = clean_markdown_formatting(line.strip())
            elements.append(Paragraph(text, styles['CustomBody']))
            
    except Exception as e:
        # If there's an error parsing a line, add it as plain text
        print(f"Warning: Error parsing line, adding as plain text: {str(e)[:50]}")
        safe_text = line.strip().replace('<', '&lt;').replace('>', '&gt;')
        elements.append(Paragraph(safe_text, styles['CustomBody']))
    
    return elements, in_code_block, in_table

def convert_markdown_to_pdf(input_file, output_file):
    """Main conversion function"""
    print(f"Converting {input_file} to PDF...")
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Setup styles
    styles = setup_styles()
    
    # Build document
    story = []
    
    # Add cover page
    story.extend(create_cover_page(styles))
    
    # Parse markdown content
    in_code_block = False
    in_table = False
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        print(f"Processing {len(lines)} lines...")
        
        for i, line in enumerate(lines):
            if i % 500 == 0 and i > 0:
                print(f"  Processed {i}/{len(lines)} lines...")
            
            elements, in_code_block, in_table = parse_markdown_line(
                line, styles, in_code_block, in_table
            )
            story.extend(elements)
        
        print("Building PDF...")
        doc.build(story)
        print(f"\nPDF created successfully: {output_file}")
        print(f"Total pages: approximately {len(lines) // 50}")
        
        return True
        
    except Exception as e:
        print(f"\nError creating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("BREWERY MANAGEMENT SYSTEM")
    print("Technical Specification PDF Generator")
    print("="*60)
    print()
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file not found: {INPUT_FILE}")
        sys.exit(1)
    
    success = convert_markdown_to_pdf(INPUT_FILE, OUTPUT_FILE)
    
    print()
    print("="*60)
    if success:
        print("PDF generation complete!")
        print(f"Output: {OUTPUT_FILE}")
    else:
        print("PDF generation failed!")
    print("="*60)
