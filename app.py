from flask import Flask, render_template, request, send_file
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import tempfile

app = Flask(__name__)

# ✅ Liste aller Nudeln (Hartweizen zuerst, dann Dinkel)
noodles = [
    "Hartweizennudeln 6mm 30% Vollkorn",
    "Casarecce",
    "Wellenspatzle",
    "Bandnudeln 9,5mm",
    "Bandnudeln 6mm",
    "Wellenbandnudeln",
    "Campanelle",
    "Spiralnudeln",
    "Spaghetti",
    "Suppennudeln",
    "Dinkelnudeln 6mm 30% Vollkorn",
    "Dinkelcasarecce",
    "Dinkelspatzle",
    "Dinkelwellenspatzle",
    "Dinkelbandnudeln 9,5mm",
    "Dinkelbandnudeln 6mm",
    "Dinkelwellenbandnudeln",
    "Dinkelcampanelle",
    "Dinkelspiralnudeln",
    "Dinkelspaghetti",
    "Dinkelsuppennudeln"
]

# ✅ Mail-Einstellungen
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
GMAIL_USER = "opasnudelbusiness@gmail.com"  # Deine Gmail-Adresse
GMAIL_PASS = "DEIN_APP_PASSWORT"  # App-Passwort von Gmail

# ✅ Empfänger-Adresse
OWNER_EMAIL = "julian.scheel97@googlemail.com"

# ✅ Route Startseite
@app.route("/")
def index():
    return render_template("index.html", noodles=noodles)

# ✅ Route zum Bestell-Absenden
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    payment = request.form.get("payment")

    # Mengen auslesen
    quantities = []
    for i in range(len(noodles)):
        qty_str = request.form.get(f"qty_{i+1}", "0")
        qty = int(qty_str) if qty_str.isdigit() else 0
        quantities.append(qty)

    # Bestellübersicht erstellen
    order_items = [(noodles[i], quantities[i]) for i in range(len(noodles)) if quantities[i] > 0]
    total_qty = sum(quantities)
    free_packs = total_qty // 10
    payable_qty = total_qty - free_packs
    total_price = payable_qty * 2.5

    # ✅ PDF erstellen
    pdf_path = create_order_pdf(name, email, payment, order_items, total_qty, free_packs, total_price)

    # ✅ E-Mails an Kunde & Shopbetreiber
    send_order_email(name, email, payment, order_items, total_qty, free_packs, total_price, pdf_path)

    # ✅ Temp-PDF löschen
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return f"Bestellung erfolgreich gesendet an {email} und Opa Nudelbusiness!"

# ✅ PDF-Erstellung mit ReportLab
def create_order_pdf(name, email, payment, order_items, total_qty, free_packs, total_price):
    fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Bestellübersicht")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Name: {name}")
    c.drawString(50, height - 100, f"Email: {email}")
    c.drawString(50, height - 120, f"Zahlungsart: {payment}")

    y = height - 160
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Nudel")
    c.drawString(300, y, "Menge")

    c.setFont("Helvetica", 12)
    y -= 20

    for item, qty in order_items:
        c.drawString(50, y, item)
        c.drawString(300, y, str(qty))
        y -= 20

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Gesamtanzahl: {total_qty} Packungen")
    y -= 20
    c.drawString(50, y, f"Gratis-Packungen: {free_packs}")
    y -= 20
    c.drawString(50, y, f"Zu zahlen: {total_price:.2f} €")

    c.save()
    return pdf_path

# ✅ E-Mail mit PDF-Anhang senden
def send_order_email(name, email, payment, order_items, total_qty, free_packs, total_price, pdf_path):
    subject = f"Nudelbestellung von {name}"
    body = f"""
Hallo {name},

vielen Dank für deine Bestellung!

Bestellübersicht:
"""
    for item, qty in order_items:
        body += f"- {item}: {qty} Stück\n"

    body += f"""
Gesamtanzahl: {total_qty} Packungen
Gratis-Packungen: {free_packs}
Zu zahlen: {total_price:.2f} €

Gewählte Zahlungsart: {payment}

Falls du per PayPal bezahlen möchtest:
➡ paypal.me/jscheel1712

Für zukünftige Bestellungen:
➡ nudelbestellung.onrender.com

Liebe Grüße
Opa Nudelbusiness
"""

    # ✅ SMTP-Versand vorbereiten
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = email
    msg["Cc"] = OWNER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    # ✅ PDF-Anhang hinzufügen
    with open(pdf_path, "rb") as f:
        pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
        pdf_attachment.add_header("Content-Disposition", "attachment", filename="Bestellübersicht.pdf")
        msg.attach(pdf_attachment)

    recipients = [email, OWNER_EMAIL]

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, recipients, msg.as_string())

if __name__ == "__main__":
    app.run(debug=True)
