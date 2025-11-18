"""
Label Printer Utility

Generates PDF labels for packaged batches with auto-populated information.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm as mm_unit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def get_label_config():
    """
    Get label configuration from local settings
    Returns default if no config found
    """
    # TODO: Load from ~/.brewerymanager/printer_config.json
    # For now, return default 100mm x 150mm
    return {
        'width_mm': 100,
        'height_mm': 150,
        'font_name': 'Helvetica',
        'font_size': 12,
        'font_size_small': 10
    }


def generate_labels_pdf(batch_data, containers, cache_manager):
    """
    Generate PDF with labels for all containers in a batch

    Args:
        batch_data: Dict with batch information (gyle, recipe, etc.)
        containers: List of dicts with container info [{name, qty, duty_volume, fill_number}, ...]
        cache_manager: Database connection to fetch recipe details

    Returns:
        str: Path to generated PDF file
    """
    # Get label configuration
    config = get_label_config()
    width = config['width_mm'] * mm_unit
    height = config['height_mm'] * mm_unit

    # Get recipe details
    cache_manager.connect()
    recipe = None
    allergens = "Not specified"
    beer_name = "Unknown"
    expected_abv = 0.0

    if batch_data.get('recipe_id'):
        recipes = cache_manager.get_all_records('recipes', f"recipe_id = '{batch_data['recipe_id']}'")
        if recipes:
            recipe = recipes[0]
            beer_name = recipe.get('recipe_name', 'Unknown')
            expected_abv = recipe.get('target_abv', 0.0)
            allergens = recipe.get('allergens', 'Not specified')
            if not allergens or allergens.strip() == '':
                allergens = "Not specified"

    cache_manager.close()

    # Create labels directory if it doesn't exist
    labels_dir = os.path.expanduser('~/.brewerymanager/labels')
    os.makedirs(labels_dir, exist_ok=True)

    # Generate filename
    gyle_number = batch_data.get('gyle_number', 'UNKNOWN')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_filename = os.path.join(labels_dir, f"{gyle_number}_labels_{timestamp}.pdf")

    # Create PDF
    c = canvas.Canvas(pdf_filename, pagesize=(width, height))

    # Calculate total number of labels
    total_labels = sum(container['qty'] for container in containers)
    current_fill = 1

    # Generate labels for each container
    for container in containers:
        container_name = container['name']
        quantity = container['qty']
        duty_volume = container['duty_volume']

        for i in range(quantity):
            # Draw label content
            draw_label(
                c=c,
                width=width,
                height=height,
                beer_name=beer_name,
                packaged_date=batch_data.get('package_date', ''),
                abv=expected_abv,
                gyle_number=gyle_number,
                fill_number=current_fill,
                total_fills=total_labels,
                duty_volume=duty_volume,
                allergens=allergens,
                config=config
            )

            current_fill += 1

            # Start new page for next label (unless it's the last one)
            if current_fill <= total_labels:
                c.showPage()

    # Save PDF
    c.save()

    print(f"✅ Generated {total_labels} labels: {pdf_filename}")
    return pdf_filename


def draw_label(c, width, height, beer_name, packaged_date, abv, gyle_number,
               fill_number, total_fills, duty_volume, allergens, config):
    """
    Draw a single label on the canvas

    Args:
        c: ReportLab canvas object
        width, height: Label dimensions
        beer_name: Name of the beer
        packaged_date: Date packaged (DD/MM/YYYY format)
        abv: Expected ABV percentage
        gyle_number: Gyle number
        fill_number: This container's number (1, 2, 3...)
        total_fills: Total number of containers
        duty_volume: Duty paid volume for this container
        allergens: Allergen information
        config: Label configuration dict
    """
    # Font settings
    font_name = config['font_name']
    font_size = config['font_size']
    font_size_small = config['font_size_small']

    # Margins and spacing
    margin = 5 * mm_unit
    line_height = font_size * 1.4
    y_position = height - margin - line_height

    # Draw border (optional, for testing)
    # c.rect(0, 0, width, height)

    # 1. Beer Name (larger, bold)
    c.setFont(font_name + "-Bold", font_size + 2)
    # Wrap beer name if too long
    max_width = width - (2 * margin)
    if c.stringWidth(beer_name, font_name + "-Bold", font_size + 2) > max_width:
        # Split into two lines if needed
        words = beer_name.split()
        line1 = words[0]
        line2 = ' '.join(words[1:]) if len(words) > 1 else ''

        c.drawString(margin, y_position, line1)
        y_position -= line_height
        if line2:
            c.drawString(margin, y_position, line2)
            y_position -= line_height
    else:
        c.drawString(margin, y_position, beer_name)
        y_position -= line_height

    y_position -= 3 * mm_unit  # Extra space after title

    # 2. Packaged Date
    c.setFont(font_name, font_size)
    c.drawString(margin, y_position, f"Packaged: {packaged_date}")
    y_position -= line_height

    # 3. ABV
    c.drawString(margin, y_position, f"ABV: {abv:.1f}%")
    y_position -= line_height

    y_position -= 3 * mm_unit  # Extra space

    # 4. Gyle Number with Fill Number
    c.drawString(margin, y_position, f"{gyle_number} / {fill_number} of {total_fills}")
    y_position -= line_height

    # 5. Duty Paid
    c.drawString(margin, y_position, f"Duty paid on {duty_volume:.1f} litres")
    y_position -= line_height

    y_position -= 3 * mm_unit  # Extra space

    # 6. Allergens (smaller font, may wrap)
    c.setFont(font_name, font_size_small)
    allergen_text = f"Allergens: {allergens}"

    # Wrap allergen text if needed
    if c.stringWidth(allergen_text, font_name, font_size_small) > max_width:
        # Simple wrapping - split at comma if possible
        if ', ' in allergens and len(allergens) > 30:
            parts = allergens.split(', ')
            c.drawString(margin, y_position, f"Allergens: {parts[0]},")
            y_position -= line_height * 0.8
            remaining = ', '.join(parts[1:])
            c.drawString(margin, y_position, remaining)
        else:
            c.drawString(margin, y_position, allergen_text)
    else:
        c.drawString(margin, y_position, allergen_text)


def open_pdf(pdf_path):
    """
    Open PDF file with default viewer

    Args:
        pdf_path: Path to PDF file
    """
    import platform
    import subprocess

    system = platform.system()

    try:
        if system == 'Windows':
            os.startfile(pdf_path)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', pdf_path])
        else:  # Linux
            subprocess.run(['xdg-open', pdf_path])

        print(f"✅ Opened PDF: {pdf_path}")
        return True
    except Exception as e:
        print(f"❌ Could not open PDF automatically: {e}")
        print(f"   Please open manually: {pdf_path}")
        return False


def print_labels_for_batch(batch_data, containers, cache_manager, auto_open=True):
    """
    High-level function to generate and optionally open label PDF

    Args:
        batch_data: Dict with batch information
        containers: List of container dicts
        cache_manager: Database connection
        auto_open: Whether to automatically open the PDF (default True)

    Returns:
        str: Path to generated PDF
    """
    pdf_path = generate_labels_pdf(batch_data, containers, cache_manager)

    if auto_open:
        open_pdf(pdf_path)

    return pdf_path
