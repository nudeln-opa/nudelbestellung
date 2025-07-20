import os
from flask import Flask, render_template, request, send_from_directory
import smtplib, ssl
from email.message import EmailMessage
from io import BytesIO

# PDF-Generierung
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

app = Flask(__name__)

# Preis pro Packung
PRICE_PER_PACK = 2.5

# Alle Nudelsorten inkl. Bild-Dateiname
noodles = [
    {"name": "Bandnudeln 6mm", "image": "Bandnudeln_6mm.JPG"},
    {"name": "Bandnudeln 6mm 30% Vollkorn", "image": "Bandnudeln_6mm_30%_Vollkorn.JPG"},
    {"name": "Bandnudeln 9,5mm", "image": "Bandnudeln_9,5mm.JPG"},
    {"name": "Campanelle", "image": "Campanelle.JPG"},
    {"name": "Casarecce", "image": "Casarecce.JPG"},
    {"name": "Dinkelbandnudeln 6mm", "image": "Dinkelbandnudeln_6mm.JPG"},
    {"name": "Dinkelbandnudeln 6mm 30% Vollkorn", "image": "Dinkelbandnudeln_6mm_30%_Vollkorn.JPG"},
    {"name": "Dinkelbandnudeln 9,5mm", "image": "Dinkelbandnudeln_9,5mm.JPG"},
    {"name": "Dinkelcampanelle", "image": "Dinkelcampanelle.JPG"},
    {"name": "Dinkelcasarecce", "image": "Dinkelcasarecce.JPG"},
    {"name": "Dinkelspaghetti", "image": "Dinkelspaghetti.JPG"},
    {"name": "Dinkelspiralnudeln", "image": "Dinkelspiralnudeln.JPG"},
    {"name": "Dinkelspätzle", "image": "Dinkelspätzle.JPG"},
    {"name": "Dinkelsuppennudeln", "image": "Dinkelsuppennudeln.JPG"},
    {"name": "Dinkelwellenbandnudeln", "image": "Dinkelwellenbandnudeln.JPG"},
    {"name": "Dinkelwellenspätzle", "image": "Dinkelwellenspätzle.JPG"},
    {"name": "Spaghetti", "image": "Spaghetti.JPG"},
    {"name": "Spiralnudeln", "image": "Spiralnudeln.JPG"},
    {"name": "Suppennudeln", "image": "Suppennudeln.JPG"},
    {"name": "Wellenbandnudeln", "image": "Wellenbandnudeln.JPG"},
    {"name": "Wellenspätzle", "image": "Wellenspätzle.JPG"},
]

# --- PDF-GENERATOR ---
def create_pdf(name, payment_method, noodles, qtys, total_qty, free_packs, total_price):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Titel & Slogan
    elements.append(Paragraph(f"<b>Nudelbestellung für {name}</b>", styles['Title']))
    elements.append(Paragraph("Nudeln wie zu Omas Zeiten – Ohne Geschmacksverstärker und Aromen", styles['Normal']))
    elements.append(Paragraph("<br/>", styles['Normal']))

    # Tabellen-Daten
    data = [["Nudelsorte (500g)", "Preis (€)", "Menge", "Summe (€)"]]
    for noodle, qty in zip(noodles, qtys):
        if qty > 0:
            data.append([noodle["name"], f"{PRICE_PER_PACK:.2f}", qty, f"{qty * PRICE_PER_PACK:.2f}"])

    # Summen
    data.append(["", "", "", ""])
    data.append(["Gesamtanzahl", "", total_qty, ""])
    data.append(["Gratis-Packungen", "", free_packs, ""])
    data.append(["Endpreis (€)", "", "", f"{total_price:.2f}"])
    data.append(["Zahlungsmethode", "", "", payment_method])

    # Tabelle erstellen
    table = Table(data, colWidths=[200, 70, 60, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route("/")
def index():
    return render_template("index.html", noodles=noodles)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    email_recipient = request.form["email"]
    payment_method = request.form.get("payment", "Bar")  # Standard Barzahlung

    # Mengen sammeln, leere = 0
    qtys = []
    for i in range(len(noodles)):
        value = request.form.get(f"qty_{i+1}", "").strip()
        qtys.append(int(value) if value.isdigit() else 0)

    total_qty = sum(qtys)

    # Gratispackungen berechnen (alle 10 eine gratis)
    free_packs = total_qty // 10

    total_price = total_qty * PRICE_PER_PACK - free_packs * PRICE_PER_PACK

    # --- PDF erstellen ---
    pdf_buffer = create_pdf(name, payment_method, noodles, qtys, total_qty, free_packs, total_price)

    # Mailinhalt
    subject = f"Nudelbestellung von {name}"
    body = f"""
Hallo {name},

vielen Dank für deine Bestellung!

Gesamtanzahl: {total_qty} Packungen
Gratis-Packungen: {free_packs}
Endpreis: {total_price:.2f} €

Gewählte Zahlungsmethode: {payment_method}
{"Bezahlen kannst du per PayPal unter: paypal.me/jscheel1712" if payment_method.lower() == "paypal" else ""}

Für zukünftige Bestellungen: https://nudelbestellung.onrender.com

Nudelige Grüße!
"""

    # Mail zusammenbauen
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "opasnudelbusiness@gmail.com"
    msg["To"] = ", ".join([email_recipient, "opasnudelbusiness@gmail.com"])
    msg.set_content(body)

    # PDF anhängen
    msg.add_attachment(
        pdf_buffer.read(),
        maintype="application",
        subtype="pdf",
        filename="Bestellung.pdf"
    )

    # Gmail SMTP
    gmail_user = "opasnudelbusiness@gmail.com"
    gmail_password = os.environ.get("GMAIL_PASSWORD")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_password)
        server.send_message(msg)

    return f"✅ Bestellung erfolgreich gesendet an {email_recipient} und Opa Nudelbusiness!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
