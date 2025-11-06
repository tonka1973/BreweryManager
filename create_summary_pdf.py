from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

# Create PDF
pdf_path = r"C:\Users\darre\Desktop\BreweryManager\Brewery_Management_System_Summary.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)

# Container for the 'Flowable' objects
elements = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1a4d2e'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading1_style = ParagraphStyle(
    'CustomHeading1',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#1a4d2e'),
    spaceAfter=12,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

heading2_style = ParagraphStyle(
    'CustomHeading2',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#2d5f3f'),
    spaceAfter=10,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

heading3_style = ParagraphStyle(
    'CustomHeading3',
    parent=styles['Heading3'],
    fontSize=12,
    textColor=colors.HexColor('#3d7f5f'),
    spaceAfter=8,
    spaceBefore=8,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=10,
    alignment=TA_JUSTIFY,
    spaceAfter=6
)

bullet_style = ParagraphStyle(
    'CustomBullet',
    parent=styles['BodyText'],
    fontSize=10,
    leftIndent=20,
    spaceAfter=4
)

# Title Page
elements.append(Spacer(1, 1.5*inch))
elements.append(Paragraph("BREWERY MANAGEMENT SYSTEM", title_style))
elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("Project Summary & Discussion Document", styles['Heading2']))
elements.append(Spacer(1, 0.3*inch))

elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d %B %Y')}", body_style))
elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("<b>Status:</b> Planning Phase Complete - Ready for Team Review", body_style))
elements.append(PageBreak())

# Executive Summary
elements.append(Paragraph("EXECUTIVE SUMMARY", heading1_style))
elements.append(Paragraph(
    "This document outlines the complete specification for a Windows desktop brewery management "
    "application designed specifically for commercial craft brewery operations. The system will provide "
    "comprehensive management of recipes, inventory, batch tracking, customer relationships, sales, "
    "invoicing, duty calculations, and label printing - all with cloud synchronization across multiple "
    "computers and offline capability.",
    body_style
))
elements.append(Spacer(1, 0.2*inch))

# Key highlights table
highlights_data = [
    ['Platform', 'Windows Desktop Application (.exe installer)'],
    ['Technology', 'Python with tkinter GUI'],
    ['Database', 'Google Sheets (cloud sync)'],
    ['Offline Mode', 'Yes - local caching with auto-sync'],
    ['Main Sections', '9 integrated modules'],
    ['Key Feature', 'Full traceability from ingredients to customer']
]

highlights_table = Table(highlights_data, colWidths=[2*inch, 4*inch])
highlights_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
]))
elements.append(highlights_table)
elements.append(Spacer(1, 0.3*inch))

# Project Overview
elements.append(Paragraph("PROJECT OVERVIEW", heading1_style))
elements.append(Paragraph(
    "The Brewery Management System is designed to replace manual spreadsheets and disconnected systems "
    "with a single, integrated application that handles all aspects of brewery operations. The system "
    "emphasizes traceability, automation, and ease of use while ensuring data is synchronized across "
    "all brewery computers.",
    body_style
))
elements.append(Spacer(1, 0.2*inch))

# Core Features - Section 1: Recipe Formulation
elements.append(Paragraph("CONFIRMED FEATURES", heading1_style))

elements.append(Paragraph("1. Recipe Formulation", heading2_style))
elements.append(Paragraph("• Recipe name, style, ABV, and batch size (scalable)", bullet_style))
elements.append(Paragraph("• Grain bill: each grain type with quantity (kg)", bullet_style))
elements.append(Paragraph("• Hops schedule: variety, quantity (g), timing (boil/dry hop)", bullet_style))
elements.append(Paragraph("• Yeast: strain and quantity needed", bullet_style))
elements.append(Paragraph("• Expected output: litres of finished beer", bullet_style))
elements.append(Paragraph("• Brewing instructions and notes section", bullet_style))
elements.append(Spacer(1, 0.1*inch))

# Section 2: Inventory Tracking
elements.append(Paragraph("2. Inventory Tracking", heading2_style))
elements.append(Paragraph("<b>Brewing Materials:</b>", heading3_style))
elements.append(Paragraph("• <b>Grain:</b> Track incoming stock (date, supplier, quantity) and usage per batch", bullet_style))
elements.append(Paragraph("• <b>Hops:</b> Track incoming stock (date, supplier, variety, quantity) and usage per batch", bullet_style))
elements.append(Paragraph("• <b>Yeast:</b> Track incoming stock (date, supplier, strain, quantity) and usage per batch", bullet_style))
elements.append(Paragraph("• <b>Sundries:</b> Track incoming items (date, item, supplier, quantity) and usage", bullet_style))
elements.append(Paragraph("• <b>Empty Casks:</b> Track returns (date in, quantity, size) and usage for filling", bullet_style))
elements.append(Spacer(1, 0.1*inch))

elements.append(Paragraph("<b>Finished Goods:</b>", heading3_style))

elements.append(Paragraph("• <b>Casks Full:</b> Beer name, gyle number, date filled, cask size, quantity", bullet_style))
elements.append(Paragraph("• <b>Casks Sold:</b> Beer name, customer, date out, quantity, cask size", bullet_style))
elements.append(Spacer(1, 0.05*inch))
elements.append(Paragraph("<b>Auto-depletion:</b> Brewing a batch automatically deducts ingredients from inventory", body_style))
elements.append(Spacer(1, 0.1*inch))

# Section 3: Batch Management
elements.append(Paragraph("3. Batch Management (Gyle Tracking)", heading2_style))
elements.append(Paragraph("• Gyle number assigned at START of batch (not at packaging)", bullet_style))
elements.append(Paragraph("• Create batch: select recipe, assign gyle, auto-deduct ingredients", bullet_style))
elements.append(Paragraph("• Status tracking: Brewing → Fermenting → Conditioning → Ready → Packaged", bullet_style))
elements.append(Paragraph("• Fermentation logs and notes", bullet_style))
elements.append(Paragraph("• Complete traceability: ingredients → batch → casks → customer", bullet_style))
elements.append(Paragraph("• Package batch: moves to finished goods with gyle number", bullet_style))
elements.append(Spacer(1, 0.1*inch))

# Section 4: Customer Management
elements.append(Paragraph("4. Customer Management (CRM)", heading2_style))
elements.append(Paragraph("• Customer database: name, contact, phone, email, address", bullet_style))
elements.append(Paragraph("• Customer notes field for general information", bullet_style))

elements.append(Paragraph("• Likes: preferred beers/styles, successful orders", bullet_style))
elements.append(Paragraph("• Dislikes: what to avoid, past issues", bullet_style))
elements.append(Paragraph("• Sales history and order frequency", bullet_style))
elements.append(Paragraph("• Outstanding invoice tracking", bullet_style))
elements.append(Paragraph("• Preferred delivery days/times", bullet_style))
elements.append(Spacer(1, 0.1*inch))

# Section 5: Sales Tools
elements.append(Paragraph("5. Sales Tools", heading2_style))
elements.append(Paragraph("• Diary/Calendar: schedule calls, deliveries, follow-ups, meetings", bullet_style))
elements.append(Paragraph("• Call log: record conversations (date, time, notes, outcome)", bullet_style))
elements.append(Paragraph("• Tasks/Reminders: follow-ups, quotes, payment chasing", bullet_style))
elements.append(Paragraph("• Sales pipeline: track opportunities (quoted → confirmed → delivered)", bullet_style))
elements.append(Spacer(1, 0.1*inch))

# Section 6: Sales/Dispatch
elements.append(Paragraph("6. Sales/Dispatch", heading2_style))
elements.append(Paragraph("• Record cask sales: customer, beer, gyle number, date out", bullet_style))
elements.append(Paragraph("• Link sales records to invoicing", bullet_style))
elements.append(Paragraph("• Sales history reporting", bullet_style))

elements.append(Paragraph("• Dispatch tracking", bullet_style))
elements.append(Spacer(1, 0.1*inch))

# Section 7: Invoicing
elements.append(Paragraph("7. Invoicing & Payment Tracking", heading2_style))
elements.append(Paragraph("• Generate invoices from sales records", bullet_style))
elements.append(Paragraph("• Auto-increment invoice numbers", bullet_style))
elements.append(Paragraph("• Line items: beer, gyle, cask size, quantity, price", bullet_style))
elements.append(Paragraph("• Subtotal, VAT (20%), and total calculations", bullet_style))
elements.append(Paragraph("• Payment tracking: Unpaid → Partially Paid → Paid", bullet_style))
elements.append(Paragraph("• Record payments (date, amount, method)", bullet_style))
elements.append(Paragraph("• Payment history per customer", bullet_style))
elements.append(Paragraph("• Outstanding balance reports", bullet_style))
elements.append(Paragraph("• Aged debt reports (30/60/90 days overdue)", bullet_style))
elements.append(Paragraph("• Print or export invoices to PDF", bullet_style))
elements.append(Spacer(1, 0.1*inch))

# Section 8: UK Duty Calculation
elements.append(Paragraph("8. UK Duty Calculation", heading2_style))
elements.append(Paragraph("• Automatic duty calculations based on ABV and volume", bullet_style))
elements.append(Paragraph("• Current UK beer duty rates (updated February 2025)", bullet_style))

elements.append(Paragraph("• Support for Draught Relief (casks/kegs 20L+)", bullet_style))
elements.append(Paragraph("• Support for Small Producer Relief (SPR) calculations", bullet_style))
elements.append(Paragraph("• Batch-level duty estimates by gyle", bullet_style))
elements.append(Paragraph("• Monthly/annual duty summaries", bullet_style))
elements.append(Paragraph("• Export duty reports for HMRC", bullet_style))
elements.append(Spacer(1, 0.1*inch))

# Section 9: Cask Label Printing
elements.append(Paragraph("9. Cask Label Printing", heading2_style))
elements.append(Paragraph("<b>Required information on labels:</b>", heading3_style))
elements.append(Paragraph("• Beer name", bullet_style))
elements.append(Paragraph("• Date packaged", bullet_style))
elements.append(Paragraph("• ABV (Alcohol by Volume)", bullet_style))
elements.append(Paragraph("• Gyle number", bullet_style))
elements.append(Paragraph("• Duty paid statement with volume", bullet_style))
elements.append(Paragraph("• Brewery logo (user uploads during setup)", bullet_style))
elements.append(Spacer(1, 0.05*inch))
elements.append(Paragraph("<b>Features:</b>", heading3_style))
elements.append(Paragraph("• Cask-appropriate sizing", bullet_style))
elements.append(Paragraph("• Professional design layout", bullet_style))

elements.append(Paragraph("• Print multiple labels per batch", bullet_style))
elements.append(Paragraph("• Export to PDF", bullet_style))
elements.append(PageBreak())

# Key Workflows
elements.append(Paragraph("KEY WORKFLOWS", heading1_style))

elements.append(Paragraph("Brewing a Batch", heading2_style))
elements.append(Paragraph("1. Create batch → select recipe → assign gyle number", body_style))
elements.append(Paragraph("2. System checks ingredient availability", body_style))
elements.append(Paragraph("3. Auto-deduct ingredients from brewing inventory", body_style))
elements.append(Paragraph("4. Track through fermentation stages (Brewing → Fermenting → Conditioning → Ready)", body_style))
elements.append(Paragraph("5. Package → moves to 'Casks Full' finished goods with gyle number", body_style))
elements.append(Paragraph("6. Print cask labels with all required information", body_style))
elements.append(Spacer(1, 0.15*inch))

elements.append(Paragraph("Selling & Invoicing", heading2_style))
elements.append(Paragraph("1. Record sale (customer, beer, gyle, quantity)", body_style))
elements.append(Paragraph("2. Auto-deduct from 'Casks Full' inventory", body_style))
elements.append(Paragraph("3. Generate invoice from sales records", body_style))
elements.append(Paragraph("4. Track payment status (Unpaid → Partially Paid → Paid)", body_style))

elements.append(Paragraph("5. Record payment when received", body_style))
elements.append(Spacer(1, 0.15*inch))

elements.append(Paragraph("Inventory Management", heading2_style))
elements.append(Paragraph("1. Log incoming brewing materials (date, supplier, quantity)", body_style))
elements.append(Paragraph("2. Brew batch → ingredients auto-deducted", body_style))
elements.append(Paragraph("3. Package → creates finished goods entries", body_style))
elements.append(Paragraph("4. Sell → auto-deduct from finished goods", body_style))
elements.append(Paragraph("5. Low stock alerts for reordering", body_style))
elements.append(PageBreak())

# Technical Specifications
elements.append(Paragraph("TECHNICAL SPECIFICATIONS", heading1_style))

tech_specs = [
    ['Platform', 'Windows Desktop Application'],
    ['Programming Language', 'Python'],
    ['User Interface', 'tkinter GUI'],
    ['Database/Storage', 'Google Sheets (cloud synchronization)'],
    ['Offline Capability', 'Yes - local caching with auto-sync when online'],
    ['Deliverable Format', 'Single .exe installer file'],
    ['Subscription Required', 'No - one-time setup only'],
    ['Multi-Computer Support', 'Yes - syncs across all brewery computers']
]

tech_table = Table(tech_specs, colWidths=[2.5*inch, 3.5*inch])
tech_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
]))
elements.append(tech_table)
elements.append(Spacer(1, 0.3*inch))

# Application Structure
elements.append(Paragraph("APPLICATION STRUCTURE (9 SECTIONS)", heading1_style))
elements.append(Paragraph("The application is organized into nine integrated sections:", body_style))
elements.append(Spacer(1, 0.1*inch))

sections = [
    "1. <b>Dashboard/Home Screen</b> - Overview, alerts, key metrics, quick actions",
    "2. <b>Recipes Section</b> - List, create, edit, and scale recipes",
    "3. <b>Inventory Section</b> - Brewing materials and finished goods tabs",
    "4. <b>Batch Management</b> - Active batches, create new, logging, packaging"
]

sections.extend([
    "5. <b>Sales & CRM</b> - Customers, diary, call log, tasks, pipeline",
    "6. <b>Sales/Dispatch</b> - Record sales, history, tracking",
    "7. <b>Invoicing</b> - Generate, manage, payment tracking, reports",
    "8. <b>Duty Calculator</b> - Monthly summaries, batch breakdowns, exports",
    "9. <b>Label Printing</b> - Select batch, generate, print cask labels"
])

for section in sections:
    elements.append(Paragraph(section, bullet_style))

elements.append(PageBreak())

# DISCUSSION POINTS - THE IMPORTANT PART FOR THE TEAM
elements.append(Paragraph("DISCUSSION POINTS FOR TEAM REVIEW", heading1_style))
elements.append(Paragraph(
    "The following areas require team discussion and decisions before development begins. "
    "These decisions will shape how the system works and ensure it meets all operational needs.",
    body_style
))
elements.append(Spacer(1, 0.2*inch))

# Discussion Point 1: UI/UX Design
elements.append(Paragraph("1. USER INTERFACE & NAVIGATION", heading2_style))
elements.append(Paragraph("<b>Questions to discuss:</b>", heading3_style))

elements.append(Paragraph("• How should users navigate between the 9 sections? (Side menu, top tabs, dashboard buttons?)", bullet_style))
elements.append(Paragraph("• What information should appear on the Dashboard home screen?", bullet_style))
elements.append(Paragraph("• What alerts are most important? (Low stock, overdue invoices, batches ready?)", bullet_style))
elements.append(Paragraph("• Should forms be multi-step wizards or single-page forms?", bullet_style))
elements.append(Paragraph("• Do you want keyboard shortcuts for common tasks?", bullet_style))
elements.append(Spacer(1, 0.15*inch))

# Discussion Point 2: Google Sheets Structure
elements.append(Paragraph("2. GOOGLE SHEETS DATABASE STRUCTURE", heading2_style))
elements.append(Paragraph("<b>Questions to discuss:</b>", heading3_style))
elements.append(Paragraph("• How many separate Google Sheets do you want? (One master sheet vs multiple sheets)", bullet_style))
elements.append(Paragraph("• How should data be organized across sheets/tabs?", bullet_style))
elements.append(Paragraph("• Who will have access to the Google Sheets? (View-only vs edit access)", bullet_style))
elements.append(Paragraph("• Should the sheets be readable by humans or optimized for the app?", bullet_style))
elements.append(Paragraph("• How often should data sync? (Real-time, every 5 minutes, on-demand?)", bullet_style))
elements.append(Spacer(1, 0.15*inch))

# Discussion Point 3: Business Rules

elements.append(Paragraph("3. BUSINESS RULES & VALIDATIONS", heading2_style))
elements.append(Paragraph("<b>Questions to discuss:</b>", heading3_style))
elements.append(Paragraph("• What stock levels should trigger 'low stock' alerts for each ingredient type?", bullet_style))
elements.append(Paragraph("• Should the system prevent brewing if ingredients are insufficient?", bullet_style))
elements.append(Paragraph("• Which fields should be required vs optional when creating records?", bullet_style))
elements.append(Paragraph("• Should invoices be locked/uneditable after sending to customers?", bullet_style))
elements.append(Paragraph("• Can batches be deleted, or only marked as 'cancelled'?", bullet_style))
elements.append(Paragraph("• What payment terms are standard? (Net 30, Net 60?)", bullet_style))
elements.append(Paragraph("• Should system prevent selling more casks than you have in stock?", bullet_style))
elements.append(Spacer(1, 0.15*inch))

# Discussion Point 4: User Permissions
elements.append(Paragraph("4. USER PERMISSIONS & SECURITY", heading2_style))
elements.append(Paragraph("<b>Questions to discuss:</b>", heading3_style))
elements.append(Paragraph("• Will multiple staff members use the system?", bullet_style))
elements.append(Paragraph("• Do different users need different permission levels?", bullet_style))
elements.append(Paragraph("• Examples: Brewing staff vs sales staff vs office/admin", bullet_style))

elements.append(Paragraph("• Should certain sections be view-only for some users?", bullet_style))
elements.append(Paragraph("• Who can delete records vs just create/edit?", bullet_style))
elements.append(Spacer(1, 0.15*inch))

# Discussion Point 5: Reporting
elements.append(Paragraph("5. REPORTS & EXPORTS", heading2_style))
elements.append(Paragraph("<b>Questions to discuss:</b>", heading3_style))
elements.append(Paragraph("• What regular reports do you need? (Weekly, monthly, annual?)", bullet_style))
elements.append(Paragraph("• Examples: Production summary, sales by customer, inventory valuation", bullet_style))
elements.append(Paragraph("• Should reports be printable, exportable to PDF, Excel, or both?", bullet_style))
elements.append(Paragraph("• What date ranges and filters are important?", bullet_style))
elements.append(Paragraph("• Do you need graphs/charts or just data tables?", bullet_style))
elements.append(Spacer(1, 0.15*inch))

# Discussion Point 6: Label Design
elements.append(Paragraph("6. CASK LABEL DESIGN SPECIFICS", heading2_style))
elements.append(Paragraph("<b>Questions to discuss:</b>", heading3_style))
elements.append(Paragraph("• What are the physical dimensions of your labels? (Width × Height in mm/inches)", bullet_style))

elements.append(Paragraph("• What printer will you use? (Model and specs)", bullet_style))
elements.append(Paragraph("• Do you have brand colors/fonts that should be used?", bullet_style))
elements.append(Paragraph("• Should brewery logo be large, small, or medium-sized?", bullet_style))
elements.append(Paragraph("• Any other mandatory information required by law or preference?", bullet_style))
elements.append(Spacer(1, 0.15*inch))

# Discussion Point 7: UK Duty
elements.append(Paragraph("7. UK DUTY CALCULATIONS", heading2_style))
elements.append(Paragraph("<b>Questions to discuss:</b>", heading3_style))
elements.append(Paragraph("• Are you registered for Small Producer Relief (SPR)?", bullet_style))
elements.append(Paragraph("• What is your annual production volume? (To determine SPR discount band)", bullet_style))
elements.append(Paragraph("• Do you sell mostly draught (casks) or packaged (bottles/cans)?", bullet_style))
elements.append(Paragraph("• Should duty calculations be per batch or aggregated monthly?", bullet_style))
elements.append(Paragraph("• What format do you need for HMRC submissions?", bullet_style))
elements.append(Spacer(1, 0.15*inch))

# Discussion Point 8: Pricing
elements.append(Paragraph("8. PRICING & COSTS", heading2_style))

elements.append(Paragraph("<b>Questions to discuss:</b>", heading3_style))
elements.append(Paragraph("• How do you currently price your beers? (Per cask size, per litre, fixed prices?)", bullet_style))
elements.append(Paragraph("• Do prices vary by customer or customer type?", bullet_style))
elements.append(Paragraph("• Should the system store ingredient costs to calculate batch costs?", bullet_style))
elements.append(Paragraph("• Do you need profitability analysis per batch or per customer?", bullet_style))
elements.append(Spacer(1, 0.15*inch))

# Discussion Point 9: Integration
elements.append(Paragraph("9. INTEGRATION WITH EXISTING SYSTEMS", heading2_style))
elements.append(Paragraph("<b>Questions to discuss:</b>", heading3_style))
elements.append(Paragraph("• Do you currently use any other software that needs to work with this system?", bullet_style))
elements.append(Paragraph("• Examples: Accounting software (Xero, QuickBooks), email systems, etc.", bullet_style))
elements.append(Paragraph("• Do you need to import existing data from spreadsheets or other systems?", bullet_style))
elements.append(Paragraph("• Should invoices sync to accounting software automatically?", bullet_style))
elements.append(PageBreak())

# Implementation Timeline
elements.append(Paragraph("IMPLEMENTATION APPROACH", heading1_style))

elements.append(Paragraph(
    "Once the team has reviewed and discussed the points above, development can proceed in phases:",
    body_style
))
elements.append(Spacer(1, 0.1*inch))

phases = [
    "<b>Phase 1: Core Setup</b> - Database structure, authentication, basic UI framework",
    "<b>Phase 2: Recipe & Inventory</b> - Recipe management and inventory tracking",
    "<b>Phase 3: Batch Management</b> - Gyle tracking and batch workflows",
    "<b>Phase 4: CRM & Sales</b> - Customer management and sales tools",
    "<b>Phase 5: Financial</b> - Invoicing, payments, and duty calculations",
    "<b>Phase 6: Reporting & Labels</b> - Reports generation and label printing",
    "<b>Phase 7: Testing & Refinement</b> - Bug fixes, optimizations, user testing",
    "<b>Phase 8: Deployment</b> - Create installer, deploy to brewery computers"
]

for phase in phases:
    elements.append(Paragraph(phase, bullet_style))

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph(
    "Each phase will be developed, tested, and reviewed before moving to the next. "
    "This approach allows for adjustments based on real-world usage and feedback.",
    body_style
))
elements.append(PageBreak())

# Benefits Summary
elements.append(Paragraph("KEY BENEFITS", heading1_style))

benefits = [
    ["Single System", "Replace multiple spreadsheets with one integrated application"],
    ["Complete Traceability", "Track from ingredients → batch → casks → customer"],
    ["Automation", "Auto-deduct inventory, auto-calculate duty, auto-generate invoices"],
    ["Cloud Sync", "All brewery computers stay synchronized via Google Sheets"],
    ["Offline Capable", "Continue working even without internet connection"],
    ["Compliance Ready", "UK duty calculations built-in with proper documentation"],
    ["Professional Output", "Generate invoices and labels that look professional"],
    ["Time Savings", "Reduce manual data entry and duplicate work"],
    ["Better Insights", "Reports and summaries for better business decisions"],
    ["Scalable", "Grows with your brewery operations"]
]

benefits_table = Table(benefits, colWidths=[1.5*inch, 4.5*inch])
benefits_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f8e9')),
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),

    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))
elements.append(benefits_table)
elements.append(PageBreak())

# Next Steps
elements.append(Paragraph("NEXT STEPS", heading1_style))
elements.append(Paragraph(
    "To move forward with this project, please complete the following:",
    body_style
))
elements.append(Spacer(1, 0.15*inch))

next_steps = [
    "<b>1. Team Review Meeting</b> - Discuss this document with all stakeholders",
    "<b>2. Answer Discussion Points</b> - Work through sections 1-9 and make decisions",
    "<b>3. Prioritize Features</b> - Confirm which features are 'must-have' vs 'nice-to-have'",
    "<b>4. Set Timeline</b> - Determine target completion dates for each phase",
    "<b>5. Approve Development</b> - Give final approval to begin building the system"
]

for step in next_steps:
    elements.append(Paragraph(step, bullet_style))

elements.append(Spacer(1, 0.3*inch))

# Contact/Notes Section
elements.append(Paragraph("MEETING NOTES & DECISIONS", heading1_style))
elements.append(Paragraph(
    "Use this space to record key decisions and notes from your team discussion:",
    body_style
))
elements.append(Spacer(1, 0.2*inch))

# Create blank note-taking space
note_lines = []
for i in range(15):
    note_lines.append(["_" * 100])

notes_table = Table(note_lines, colWidths=[6*inch])
notes_table.setStyle(TableStyle([
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
]))
elements.append(notes_table)

# Footer
elements.append(Spacer(1, 0.3*inch))
elements.append(Paragraph(
    "<i>This document was automatically generated for the Brewery Management System project. "
    "For questions or clarifications, please contact the development team.</i>",
    ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
))

# Build PDF

doc.build(elements)
print(f"PDF created successfully: {pdf_path}")
