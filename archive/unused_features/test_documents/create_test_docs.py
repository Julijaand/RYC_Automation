"""
Generate test documents for RYC Automation testing
Creates invoice, payroll, facture, and fiche de paie samples in PDF, JPG, PNG
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image, ImageDraw, ImageFont
import os

# Create output directory
os.makedirs("generated", exist_ok=True)

def create_invoice_pdf():
    """Create English invoice PDF"""
    c = canvas.Canvas("generated/Invoice_2025_003_TEST.pdf", pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, height - 1*inch, "INVOICE")
    
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 1.5*inch, "Invoice Number: INV-2025-003")
    c.drawString(1*inch, height - 1.8*inch, "Date: January 3, 2025")
    
    # Company details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 2.5*inch, "From:")
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 2.8*inch, "ABC Services Ltd")
    c.drawString(1*inch, height - 3.0*inch, "123 Business Street")
    c.drawString(1*inch, height - 3.2*inch, "Paris, France")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 3.8*inch, "Bill To:")
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 4.1*inch, "Client Name: Liu Yang")
    c.drawString(1*inch, height - 4.3*inch, "Company: Yang Enterprises SARL")
    c.drawString(1*inch, height - 4.5*inch, "789 Business Blvd, Nice, France")
    
    # Items
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 5.2*inch, "Description")
    c.drawString(4.5*inch, height - 5.2*inch, "Amount")
    c.line(1*inch, height - 5.3*inch, 6*inch, height - 5.3*inch)
    
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 5.6*inch, "Accounting Services - January 2025")
    c.drawString(4.5*inch, height - 5.6*inch, "€1,800.00")
    
    c.drawString(1*inch, height - 5.9*inch, "Tax Consulting")
    c.drawString(4.5*inch, height - 5.9*inch, "€950.00")
    
    c.line(1*inch, height - 6.1*inch, 6*inch, height - 6.1*inch)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(3.5*inch, height - 6.5*inch, "Total:")
    c.drawString(4.5*inch, height - 6.5*inch, "€2,750.00")
    
    c.save()
    print("✅ Created: Invoice_2025_003_TEST.pdf")

def create_facture_pdf():
    """Create French invoice (facture) PDF"""
    c = canvas.Canvas("generated/Facture_2025_008_TEST.pdf", pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, height - 1*inch, "FACTURE")
    
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 1.5*inch, "Numéro: FA-2025-008")
    c.drawString(1*inch, height - 1.8*inch, "Date: 3 Janvier 2025")
    
    # Company details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 2.5*inch, "De:")
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 2.8*inch, "RYC Conseil SARL")
    c.drawString(1*inch, height - 3.0*inch, "15 Rue de la Comptabilité")
    c.drawString(1*inch, height - 3.2*inch, "75001 Paris, France")
    c.drawString(1*inch, height - 3.4*inch, "SIRET: 123 456 789 00012")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 4.1*inch, "À:")
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 4.4*inch, "Client: Zhang Li")
    c.drawString(1*inch, height - 4.6*inch, "Société: Li Consulting SARL")
    c.drawString(1*inch, height - 4.8*inch, "45 Rue de Commerce, Toulouse")
    
    # Items
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 5.5*inch, "Désignation")
    c.drawString(4.5*inch, height - 5.5*inch, "Montant")
    c.line(1*inch, height - 5.6*inch, 6*inch, height - 5.6*inch)
    
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 5.9*inch, "Services de comptabilité - Janvier 2025")
    c.drawString(4.5*inch, height - 5.9*inch, "2 100,00 €")
    
    c.drawString(1*inch, height - 6.2*inch, "TVA 20%")
    c.drawString(4.5*inch, height - 6.2*inch, "420,00 €")
    
    c.line(1*inch, height - 6.4*inch, 6*inch, height - 6.4*inch)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(3.5*inch, height - 6.8*inch, "Total TTC:")
    c.drawString(4.5*inch, height - 6.8*inch, "2 520,00 €")
    
    c.save()
    print("✅ Created: Facture_2025_008_TEST.pdf")

def create_payroll_jpg():
    """Create English payroll document as JPG"""
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use default font
    try:
        from PIL import ImageFont
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        font_normal = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        font_title = ImageFont.load_default()
        font_normal = ImageFont.load_default()
    
    # Title
    draw.text((50, 30), "PAYROLL STATEMENT", fill='black', font=font_title)
    draw.line([(50, 70), (750, 70)], fill='black', width=2)
    
    # Employee info
    y = 100
    draw.text((50, y), "Employee: Zhou Min", fill='black', font=font_normal)
    draw.text((50, y+30), "Employee ID: EMP-2025-022", fill='black', font=font_normal)
    draw.text((50, y+60), "Pay Period: January 2025", fill='black', font=font_normal)
    draw.text((50, y+90), "Payment Date: January 31, 2025", fill='black', font=font_normal)
    
    # Earnings
    y = 320
    draw.text((50, y), "Earnings:", fill='black', font=font_title)
    draw.line([(50, y+30), (750, y+30)], fill='black', width=1)
    draw.text((50, y+50), "Base Salary", fill='black', font=font_normal)
    draw.text((600, y+50), "€3,800.00", fill='black', font=font_normal)
    
    # Deductions
    y = 450
    draw.text((50, y), "Deductions:", fill='black', font=font_title)
    draw.line([(50, y+30), (750, y+30)], fill='black', width=1)
    draw.text((50, y+50), "Social Security", fill='black', font=font_normal)
    draw.text((600, y+50), "€494.00", fill='black', font=font_normal)
    draw.text((50, y+80), "Income Tax", fill='black', font=font_normal)
    draw.text((600, y+80), "€420.00", fill='black', font=font_normal)
    
    # Net pay
    y = 650
    draw.line([(50, y), (750, y)], fill='black', width=2)
    draw.text((50, y+20), "NET PAY:", fill='black', font=font_title)
    draw.text((600, y+20), "€2,886.00", fill='black', font=font_title)
    
    img.save("generated/Payroll_Jan2025_ZhouMin_TEST.jpg", "JPEG")
    print("✅ Created: Payroll_Jan2025_ZhouMin_TEST.jpg")

def create_fiche_paie_png():
    """Create French payroll slip (fiche de paie) as PNG"""
    img = Image.new('RGB', (800, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        font_normal = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    except:
        font_title = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Title
    draw.text((50, 30), "FICHE DE PAIE", fill='black', font=font_title)
    draw.line([(50, 70), (750, 70)], fill='black', width=2)
    
    # Employer
    y = 100
    draw.text((50, y), "Employeur:", fill='black', font=font_normal)
    draw.text((50, y+25), "RYC Conseil SARL", fill='black', font=font_small)
    draw.text((50, y+45), "SIRET: 123 456 789 00012", fill='black', font=font_small)
    
    # Employee
    draw.text((400, y), "Salarié:", fill='black', font=font_normal)
    draw.text((400, y+25), "Wu Fang", fill='black', font=font_small)
    draw.text((400, y+45), "N° Sécu: 2 88 05 92 234 567 89", fill='black', font=font_small)
    
    # Period
    y = 220
    draw.text((50, y), "Période: Janvier 2025", fill='black', font=font_normal)
    draw.text((400, y), "Date de paiement: 31/01/2025", fill='black', font=font_normal)
    
    # Salary details
    y = 280
    draw.line([(50, y), (750, y)], fill='black', width=1)
    draw.text((50, y+10), "Libellé", fill='black', font=font_normal)
    draw.text((400, y+10), "Base", fill='black', font=font_normal)
    draw.text((600, y+10), "Montant", fill='black', font=font_normal)
    draw.line([(50, y+40), (750, y+40)], fill='black', width=1)
    
    # Gross salary
    draw.text((50, y+50), "Salaire de base", fill='black', font=font_small)
    draw.text((400, y+50), "151.67 h", fill='black', font=font_small)
    draw.text((600, y+50), "3 200,00 €", fill='black', font=font_small)
    
    # Contributions
    y = 380
    draw.text((50, y), "Cotisations salariales:", fill='black', font=font_normal)
    draw.text((50, y+30), "Sécurité sociale", fill='black', font=font_small)
    draw.text((600, y+30), "- 224,00 €", fill='black', font=font_small)
    draw.text((50, y+55), "Retraite complémentaire", fill='black', font=font_small)
    draw.text((600, y+55), "- 96,00 €", fill='black', font=font_small)
    draw.text((50, y+80), "Chômage", fill='black', font=font_small)
    draw.text((600, y+80), "- 76,80 €", fill='black', font=font_small)
    draw.text((50, y+105), "CSG-CRDS", fill='black', font=font_small)
    draw.text((600, y+105), "- 264,00 €", fill='black', font=font_small)
    
    # Net salary
    y = 550
    draw.line([(50, y), (750, y)], fill='black', width=2)
    draw.text((50, y+20), "Salaire brut:", fill='black', font=font_normal)
    draw.text((600, y+20), "3 200,00 €", fill='black', font=font_normal)
    draw.text((50, y+50), "Total cotisations:", fill='black', font=font_normal)
    draw.text((600, y+50), "- 660,80 €", fill='black', font=font_normal)
    draw.line([(50, y+80), (750, y+80)], fill='black', width=2)
    draw.text((50, y+100), "SALAIRE NET:", fill='black', font=font_title)
    draw.text((550, y+100), "2 539,20 €", fill='black', font=font_title)
    
    img.save("generated/Fiche_Paie_Jan2025_WuFang_TEST.png", "PNG")
    print("✅ Created: Fiche_Paie_Jan2025_WuFang_TEST.png")

def create_contract_pdf():
    """Create employment contract PDF"""
    c = canvas.Canvas("generated/Contract_Employment_2025_001_TEST.pdf", pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 80, "EMPLOYMENT CONTRACT")
    
    # Contract number and date
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 120, "Contract No: EMP-2025-001")
    c.drawString(400, height - 120, "Date: January 15, 2025")
    
    # Line separator
    c.line(50, height - 135, width - 50, height - 135)
    
    # Parties section
    y = height - 170
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "PARTIES TO THIS AGREEMENT")
    
    c.setFont("Helvetica", 10)
    y -= 30
    c.drawString(50, y, "Employer:")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(120, y, "RYC Conseil Ltd.")
    c.setFont("Helvetica", 10)
    y -= 20
    c.drawString(120, y, "Company Registration: 12345678")
    y -= 15
    c.drawString(120, y, "Address: 123 Business Street, Paris, France")
    
    y -= 35
    c.drawString(50, y, "Employee:")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(120, y, "Chen Li")
    c.setFont("Helvetica", 10)
    y -= 20
    c.drawString(120, y, "Social Security No: 1 89 06 75 123 456 78")
    y -= 15
    c.drawString(120, y, "Address: 45 Rue de la République, Paris, France")
    
    # Terms section
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "TERMS AND CONDITIONS")
    
    c.setFont("Helvetica", 10)
    y -= 30
    c.drawString(50, y, "1. Position:")
    c.drawString(150, y, "Senior Business Consultant")
    
    y -= 25
    c.drawString(50, y, "2. Start Date:")
    c.drawString(150, y, "February 1, 2025")
    
    y -= 25
    c.drawString(50, y, "3. Contract Type:")
    c.drawString(150, y, "Permanent Full-Time Employment (CDI)")
    
    y -= 25
    c.drawString(50, y, "4. Salary:")
    c.drawString(150, y, "€4,200.00 gross per month")
    
    y -= 25
    c.drawString(50, y, "5. Working Hours:")
    c.drawString(150, y, "35 hours per week")
    
    y -= 25
    c.drawString(50, y, "6. Annual Leave:")
    c.drawString(150, y, "25 working days per year")
    
    y -= 25
    c.drawString(50, y, "7. Notice Period:")
    c.drawString(150, y, "3 months")
    
    y -= 25
    c.drawString(50, y, "8. Probation Period:")
    c.drawString(150, y, "3 months")
    
    # Responsibilities section
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "RESPONSIBILITIES")
    
    c.setFont("Helvetica", 10)
    y -= 25
    c.drawString(50, y, "• Provide strategic business consulting services to clients")
    y -= 20
    c.drawString(50, y, "• Manage client relationships and project deliveries")
    y -= 20
    c.drawString(50, y, "• Prepare business reports and presentations")
    y -= 20
    c.drawString(50, y, "• Comply with all company policies and procedures")
    
    # Additional terms
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "ADDITIONAL TERMS")
    
    c.setFont("Helvetica", 9)
    y -= 25
    c.drawString(50, y, "This contract is governed by French labor law. The employee agrees to maintain confidentiality")
    y -= 15
    c.drawString(50, y, "regarding all business matters and client information. Benefits include health insurance coverage")
    y -= 15
    c.drawString(50, y, "and participation in the company pension scheme according to statutory requirements.")
    
    # Signatures
    y -= 60
    c.line(50, y, 250, y)
    c.line(350, y, 550, y)
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Employer Signature")
    c.drawString(350, y, "Employee Signature")
    y -= 15
    c.drawString(50, y, "Date: _______________")
    c.drawString(350, y, "Date: _______________")
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 30, "RYC Conseil Ltd. | 123 Business Street, Paris | contact@ryc-conseil.fr")
    
    c.save()
    print("✅ Created: Contract_Employment_2025_001_TEST.pdf")

def create_receipt_pdf():
    """Create receipt PDF"""
    c = canvas.Canvas("generated/Receipt_2025_045_TEST.pdf", pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 80, "RECEIPT")
    
    # Receipt info
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 130, "Receipt No: RCP-2025-045")
    c.drawString(400, height - 130, "Date: January 10, 2025")
    
    # Line separator
    c.line(50, height - 145, width - 50, height - 145)
    
    # Vendor details
    y = height - 180
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Vendor Information")
    
    c.setFont("Helvetica", 10)
    y -= 25
    c.drawString(50, y, "Office Supplies Pro")
    y -= 18
    c.drawString(50, y, "56 Rue du Commerce")
    y -= 18
    c.drawString(50, y, "75015 Paris, France")
    y -= 18
    c.drawString(50, y, "SIRET: 987 654 321 00034")
    y -= 18
    c.drawString(50, y, "VAT: FR12987654321")
    
    # Customer
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Bill To")
    
    c.setFont("Helvetica", 10)
    y -= 25
    c.drawString(50, y, "RYC Conseil SARL")
    y -= 18
    c.drawString(50, y, "15 Rue de la Comptabilité")
    y -= 18
    c.drawString(50, y, "75001 Paris, France")
    
    # Items table
    y -= 50
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Description")
    c.drawString(350, y, "Qty")
    c.drawString(420, y, "Unit Price")
    c.drawString(500, y, "Total")
    
    y -= 5
    c.line(50, y, width - 50, y)
    
    # Line items
    c.setFont("Helvetica", 10)
    y -= 25
    c.drawString(50, y, "Office Paper A4 (5 reams)")
    c.drawString(350, y, "5")
    c.drawString(420, y, "€4.50")
    c.drawString(500, y, "€22.50")
    
    y -= 20
    c.drawString(50, y, "Blue Pens (Box of 50)")
    c.drawString(350, y, "2")
    c.drawString(420, y, "€8.90")
    c.drawString(500, y, "€17.80")
    
    y -= 20
    c.drawString(50, y, "Stapler Heavy Duty")
    c.drawString(350, y, "1")
    c.drawString(420, y, "€15.60")
    c.drawString(500, y, "€15.60")
    
    y -= 20
    c.drawString(50, y, "File Folders (Pack of 25)")
    c.drawString(350, y, "3")
    c.drawString(420, y, "€6.70")
    c.drawString(500, y, "€20.10")
    
    y -= 20
    c.drawString(50, y, "Sticky Notes Assorted Colors")
    c.drawString(350, y, "4")
    c.drawString(420, y, "€3.25")
    c.drawString(500, y, "€13.00")
    
    # Subtotal and tax
    y -= 35
    c.line(420, y, width - 50, y)
    
    y -= 25
    c.setFont("Helvetica", 11)
    c.drawString(420, y, "Subtotal:")
    c.drawString(500, y, "€89.00")
    
    y -= 22
    c.drawString(420, y, "VAT (20%):")
    c.drawString(500, y, "€17.80")
    
    y -= 5
    c.line(420, y, width - 50, y)
    
    # Total
    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(420, y, "TOTAL:")
    c.drawString(490, y, "€106.80")
    
    # Payment method
    y -= 50
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Payment Method: Credit Card ending in ****4567")
    y -= 18
    c.drawString(50, y, "Transaction ID: TXN-2025-0110-8934")
    
    # Footer
    y -= 50
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width/2, y, "Thank you for your business!")
    
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 40, "Office Supplies Pro | Tel: +33 1 45 67 89 00 | Email: contact@officesuppliespro.fr")
    c.drawCentredString(width/2, 25, "For questions about this receipt, please contact us within 30 days")
    
    c.save()
    print("✅ Created: Receipt_2025_045_TEST.pdf")

def create_notification_letter_pdf():
    """Create notification letter - completely different from financial docs"""
    c = canvas.Canvas("generated/Notification_Office_Closure_2025_TEST.pdf", pagesize=letter)
    width, height = letter
    
    # Company letterhead
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 70, "RYC CONSEIL SARL")
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, height - 88, "15 Rue de la Comptabilité, 75001 Paris, France")
    c.drawCentredString(width/2, height - 102, "Tel: +33 1 23 45 67 89 | Email: contact@ryc-conseil.fr")
    
    # Line separator
    c.line(50, height - 120, width - 50, height - 120)
    
    # Date and reference
    y = height - 160
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Date: January 12, 2025")
    c.drawString(50, y - 18, "Ref: NOTIF-2025-001")
    
    # Title
    y -= 70
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y, "OFFICIAL NOTIFICATION")
    c.drawCentredString(width/2, y - 22, "OFFICE CLOSURE - PUBLIC HOLIDAY")
    
    # Salutation
    y -= 70
    c.setFont("Helvetica", 11)
    c.drawString(50, y, "Dear Valued Clients and Partners,")
    
    # Body paragraphs
    y -= 35
    c.setFont("Helvetica", 10)
    
    # Paragraph 1
    text1 = "We would like to inform you that our office will be closed on the following dates"
    c.drawString(50, y, text1)
    y -= 15
    c.drawString(50, y, "due to public holidays and annual maintenance:")
    
    y -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(70, y, "• Friday, January 31, 2025 - National Holiday")
    y -= 18
    c.drawString(70, y, "• Monday, February 3, 2025 - Annual System Maintenance")
    y -= 18
    c.drawString(70, y, "• Tuesday, February 4, 2025 - Staff Training Day")
    
    # Paragraph 2
    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "During this period, our offices will be completely closed and no staff will be available")
    y -= 15
    c.drawString(50, y, "to respond to inquiries. We apologize for any inconvenience this may cause.")
    
    # Paragraph 3
    y -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Emergency Contact Information:")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "For urgent matters only, please contact our emergency hotline:")
    y -= 18
    c.drawString(70, y, "Emergency: +33 6 12 34 56 78 (Available 9 AM - 6 PM)")
    y -= 15
    c.drawString(70, y, "Email: emergency@ryc-conseil.fr")
    
    # Paragraph 4
    y -= 30
    c.drawString(50, y, "Regular operations will resume on Wednesday, February 5, 2025 at 9:00 AM.")
    y -= 15
    c.drawString(50, y, "All pending matters will be addressed promptly upon our return.")
    
    # Paragraph 5
    y -= 30
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, "Please note: Any documents or inquiries received during the closure period will be")
    y -= 15
    c.drawString(50, y, "processed in the order they were received starting February 5, 2025.")
    
    # Closing
    y -= 40
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Thank you for your understanding and continued partnership.")
    
    y -= 35
    c.drawString(50, y, "Sincerely,")
    
    y -= 50
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Marie Dubois")
    y -= 18
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "General Manager")
    y -= 15
    c.drawString(50, y, "RYC Conseil SARL")
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 50, "This is an official notification from RYC Conseil SARL")
    c.drawCentredString(width/2, 35, "SIRET: 123 456 789 00012 | RCS Paris B 123 456 789")
    
    c.save()
    print("✅ Created: Notification_Office_Closure_2025_TEST.pdf")

if __name__ == "__main__":
    print("Generating test documents...")
    print()
    
    create_invoice_pdf()
    create_facture_pdf()
    create_payroll_jpg()
    create_fiche_paie_png()
    create_contract_pdf()
    create_receipt_pdf()
    create_notification_letter_pdf()
    
    print()
    print("=" * 60)
    print("✅ All test documents created in 'generated' folder!")
    print("=" * 60)
    print()
    print("📧 Next steps:")
    print("1. Email these NEW test files to yourself with relevant subjects:")
    print("   - 'Invoice for January services' + Invoice_2025_003_TEST.pdf")
    print("   - 'Facture janvier' + Facture_2025_008_TEST.pdf")
    print("   - 'Payroll statement January' + Payroll_Jan2025_ZhouMin_TEST.jpg")
    print("   - 'Fiche de paie janvier' + Fiche_Paie_Jan2025_WuFang_TEST.png")
    print("   - 'Employment Contract' + Contract_Employment_2025_001_TEST.pdf")
    print("   - 'Office supplies receipt' + Receipt_2025_045_TEST.pdf")
    print("   - 'Important notification' + Notification_Office_Closure_2025_TEST.pdf")
    print()
    print("2. Run the automation:")
    print("   python -m src.main")
