import os
from flask import Flask, render_template, request
import smtplib, ssl, io
from email.message import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# ✅ Nudelsorten-Liste (ohne Sonderzeichen in Bildnamen)
noodles = [
    "Hartweizennudeln 6mm 30% Vollkorn",
    "Casarecce",
    "Wellenspätzle",
    "Bandnudeln 9,5mm",
    "Bandnudeln 6mm",
    "Wellenbandnudeln",
    "Campanelle",
    "Spiralnudeln",
    "Spaghetti",
    "Suppennudeln",
    "Dinkelnudeln 6mm 30% Vollkorn",
    "Dinkelcasarecce",
    "Dinkelspätzle",
    "Dinkelwellenspätzle",
    "Dinkelbandnudeln 9,5mm",
    "Dinkelbandnudeln 6mm",
    "Dinkelwellenbandnudeln",
    "Dinkelcampanelle",
    "Dinkelspiralnudeln",
    "Dinkelspaghetti",
    "Dinkelsuppennudeln"
]

@app.route("/")
def index():
    return render_template("index.html", noodles=noodles)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "Unbekannt")
    email_recipient = request.form.get("email")
    payment_method = request.form.get("payment_method", "Bar")

    qtys = [int(request.form.get(f"qty_{i}", 0) or 0) for i in range(1, len(noodles) + 1)]
    total_qty = sum(qtys)

    # Gratis-Packungen (alle 10 -> 1 gratis)
    free_packs = total_qty // 10

    price_per_pack = 2.5
    total_price = total_qty * price_per_pack - free_packs * price_per_pack

    # ✅ PDF mit Bestellung erzeugen
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Nudelbestellung von {name}")
    y -= 30

    c.setFont("Helvetica", 12)
    for noodle, qty in zip(noodles, qtys):
        if qty > 0:
            c.drawString(50, y, f"{noodle} - {qty} x {price_per_pack:.2f} € = {qty * price_per_pack:.2f} €")
            y -= 20

    y -= 20
    c.drawString(50, y, f"Gesamtanzahl: {total_qty} Packungen")
    y -= 20
    c.drawString(50, y, f"Gratis-Packungen: {free_packs}")
    y -= 20
    c.drawString(50, y, f"Endpreis: {total_price:.2f} €")
    y -= 30
    c.drawString(50, y, f"Bezahlmethode: {payment_method}")
    y -= 30
    c.drawString(50, y, "Vielen Dank für Ihre Bestellung!")
    c.save()

    pdf_buffer.seek(0)

    # ✅ Email-Inhalt
    subject = f"Nudelbestellung von {name}"
    body = f"""Hallo {name},

vielen Dank für deine Bestellung!

Gesamtanzahl: {total_qty} Packungen
Gratis-Packungen: {free_packs}
Endpreis: {total_price:.2f} €
Bezahlmethode: {payment_method}

"""

    # PayPal-Link nur, wenn ausgewählt
    if payment_method == "PayPal":
        body += "Hier kannst du bequem per PayPal bezahlen: paypal.me/jscheel1712\n\n"

    body += "Für zukünftige Bestellungen besuche: https://nudelbestellung.onrender.com\n\nLiebe Grüße,\nOpa Nudelbusiness"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "opasnudelbusiness@gmail.com"
    msg["To"] = ", ".join([email_recipient, "opasnudelbusiness@gmail.com"])
    msg.set_content(body)

    # PDF anhängen
    msg.add_attachment(pdf_buffer.read(), maintype="application", subtype="pdf", filename="Bestellung.pdf")

    gmail_user = "opasnudelbusiness@gmail.com"
    gmail_password = os.environ.get("GMAIL_PASSWORD")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_password)
        server.send_message(msg)

    return f"✅ Bestellung erfolgreich gesendet an {email_recipient} und Opa Nudelbusiness!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
