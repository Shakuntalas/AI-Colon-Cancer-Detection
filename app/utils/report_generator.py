import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
import uuid
import datetime

def generate_pdf_report(prediction_result, original_image_path, heatmap_path, output_dir):
    """
    Generate a professional hospital-style PDF report for the AI prediction.
    
    Parameters
    ----------
    prediction_result : dict
        Dictionary containing prediction results (class, confidence, probabilities)
    original_image_path : str
        Path to the uploaded image.
    heatmap_path : str
        Path to the Grad-CAM heatmap.
    output_dir : str
        Directory to save the PDF.
        
    Returns
    -------
    str
        Absolute path to the generated PDF.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
    pdf_path = os.path.join(output_dir, filename)
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=1,
        fontSize=18,
        textColor=colors.HexColor('#2c3e50')
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    
    elements = []
    
    # Header
    elements.append(Paragraph("ColonSightAI - Diagnostic Report", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Date
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"<b>Date:</b> {date_str}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Prediction Results
    diagnosis = prediction_result.get('display_name', 'Unknown')
    confidence = prediction_result.get('confidence', 0.0)
    
    elements.append(Paragraph("<b>AI Analysis Results</b>", styles['Heading2']))
    
    res_data = [
        ["Predicted Class:", diagnosis],
        ["Confidence Score:", f"{confidence * 100:.2f}%"]
    ]
    
    t = Table(res_data, colWidths=[2 * inch, 4 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Images (Original and Heatmap side by side)
    elements.append(Paragraph("<b>Tissue Sample & AI Heatmap (Grad-CAM)</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.1 * inch))
    
    img_data = []
    row = []
    
    try:
        orig_img = Image(original_image_path, width=2.5*inch, height=2.5*inch)
        row.append(orig_img)
    except Exception:
        row.append("Original Image Missing")
        
    try:
        heat_img = Image(heatmap_path, width=2.5*inch, height=2.5*inch)
        row.append(heat_img)
    except Exception:
        row.append("Heatmap Missing")
        
    img_data.append(row)
    img_data.append(["Original Sample", "AI Activation Heatmap"])
    
    img_table = Table(img_data, colWidths=[3 * inch, 3 * inch])
    img_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Oblique'),
    ]))
    
    elements.append(img_table)
    elements.append(Spacer(1, 0.4 * inch))
    
    # Recommendation
    elements.append(Paragraph("<b>Recommendation</b>", styles['Heading2']))
    if 'Adenocarcinoma' in diagnosis:
        rec_text = "The AI model has detected patterns consistent with Colon Adenocarcinoma. It is highly recommended that these results be reviewed by an expert pathologist immediately."
    else:
        rec_text = "The AI model has detected patterns consistent with Normal Colon Tissue. Standard screening protocols should be maintained."
        
    elements.append(Paragraph(rec_text, normal_style))
    elements.append(Spacer(1, 0.5 * inch))
    
    # Disclaimer
    disclaimer = ("DISCLAIMER: ColonSightAI is an experimental AI tool meant to assist pathologists. "
                  "It should not be used as the sole basis for clinical diagnosis. Always consult a qualified medical professional.")
    elements.append(Paragraph(f"<i>{disclaimer}</i>", normal_style))
    
    doc.build(elements)
    
    return pdf_path
