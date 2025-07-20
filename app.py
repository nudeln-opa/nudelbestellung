import os
from flask import Flask, render_template, request
import smtplib, ssl, io
from email.message import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

# ✅ Getrennte Listen für Hartweizen & Dinkel
hartweizen_noodles = [
    "Hartweizennudeln 6mm 30% Vollkorn",
    "Casarecce",
    "Wellenspätzle",
    "Bandnudeln 9,5mm",
    "Bandnudeln 6mm",
    "Wellenbandnudeln",
    "Campanelle",
    "Spiralnudeln",
    "Spaghetti",
    "Suppennudeln"
]

dinkel_noodles = [
    "Dinkelnudeln 6mm 30% Vollkorn",
    "Dinkelcasarecce",
    "Dinkelwellenspätzle",
    "Dinkelbandnudeln 9,5mm",
    "Dinkelbandnudeln 6mm",
    "Dinkelwellenbandnudeln",
    "Dinkelcampanelle",
    "Dinkelspiralnudeln",
    "Dinkelspaghetti",
    "Dinkelsuppennudeln"
]

PRICE = 2.5

@app.route("/")
def index():
    return render_template("index.html",
                           hartweizen_noodles=hartweizen_noodles,
                           dinkel_noodles=dinkel_noodles,
                           price=PRICE)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email_recipient = request.form.get("email")
    payment_method = request.form.get("payment_method")

    # ✅ Alle Mengen als Integer holen (Hartweizen + Dinkel)
    all_noodles = hartweizen_noodles + dinkel_noodles
    quantities = [int(request.form.get(f"qty_{i}", 0)) for i in range(len(all_noodles))]

    # ✅ Gesamtmenge berechnen
    total_qty = sum(quantities)

    # ✅ Gratis-Packungen berechnen
    free_packs = total_qty // 10  

    # ✅ Gesamtpreis berechnen
    total_price = total_qty * PRICE - free_packs * PRICE

    # ✅ PDF erzeugen
    pdf_data = io.BytesIO()
    c = canvas.Canvas(pdf_data, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, f"Nudelbestellung von {name}")
    c.setFont("Helvetica", 10)
    y = 770
    for noodle, qty in zip(all_noodles, quantities):
        if qty > 0:
            c.drawString(50, y, f"{noodle} - Menge: {qty} - {qty * PRICE:.2f} €")
            y -= 20

    y -= 20
    c.drawString(50, y, f"Gesamtanzahl: {total_qty}")
    y -= 20
    c.drawString(50, y, f"Gratis-Packungen: {free_packs}")
    y -= 20
    c.drawString(50, y, f"Endpreis: {total_price:.2f} €")
    y -= 40
    c.drawString(50, y, f"Zahlungsmethode: {payment_method}")
    y -= 20
    c.drawString(50, y, "PayPal-Link: paypal.me/jscheel1712")
    y -= 20
    c.drawString(50, y, "Für künftige Bestellungen: nudelbestellung.onrender.com")

    c.save()
    pdf_data.seek(0)

    # ✅ Mail vorbereiten
    subject = f"Nudelbestellung von {name}"
    body = f"""
Hallo {name},

vielen Dank für deine Bestellung.

✅ Gesamtanzahl: {total_qty} Packungen  
✅ Gratis-Packungen: {free_packs}  
✅ Endpreis: {total_price:.2f} €  
✅ Zahlungsmethode: {payment_method}

📌 Für PayPal: paypal.me/jscheel1712  
📌 Für künftige Bestellungen: nudelbestellung.onrender.com  

Liebe Grüße,  
Opa Nudelbusiness
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "opasnudelbusiness@gmail.com"
    msg["To"] = ", ".join([email_recipient, "opasnudelbusiness@gmail.com"])
    msg.set_content(body)

    # PDF anhängen
    msg.add_attachment(pdf_data.read(), maintype="application", subtype="pdf", filename="Bestellung.pdf")

    # SMTP senden
    gmail_user = "opasnudelbusiness@gmail.com"
    gmail_password = os.environ.get("GMAIL_PASSWORD")
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_password)
        server.send_message(msg)

    return f"✅ Bestellung erfolgreich gesendet an {email_recipient} und Opa Nudelbusiness!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
