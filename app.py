from flask import Flask, render_template, request, url_for
import smtplib, ssl, io, os
from email.message import EmailMessage
import openpyxl

app = Flask(__name__)

# PayPal-Mail
PAYPAL_MAIL = "opasnudelbusiness@gmail.com"
PRICE_PER_PACK = 2.5

# Nudelsorten + Bilddateien
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

@app.route("/")
def index():
    return render_template("index.html", noodles=noodles, price_per_pack=PRICE_PER_PACK, paypal=PAYPAL_MAIL)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    email_recipient = request.form["email"]
    qtys = [int(request.form.get(f"qty_{i}", 0)) for i in range(len(noodles))]
    total_qty = sum(qtys)

    # Gratis-Packungen: 1 gratis pro 10 bestellte
    free_packs = total_qty // 10
    total_price = total_qty * PRICE_PER_PACK - free_packs * PRICE_PER_PACK

    # Excel-Datei
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bestellung"
    ws.column_dimensions['A'].width = 40  # Spalte A breiter machen
    ws.append(["Nudelsorte", "Preis (€)", "Menge", "Summe (€)"])
    for noodle, qty in zip(noodles, qtys):
        if qty > 0:
            ws.append([noodle["name"], PRICE_PER_PACK, qty, qty * PRICE_PER_PACK])
    ws.append([])
    ws.append(["Gesamtanzahl", total_qty])
    ws.append(["Gratis-Packungen", free_packs])
    ws.append(["Endpreis (€)", total_price])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    subject = f"Nudelbestellung von {name}"
    body = f"""Danke für deine Bestellung, {name}!

Gesamtanzahl: {total_qty} Packungen
Gratis-Packungen: {free_packs}
Endpreis: {total_price:.2f} €

Bitte überweise den Betrag an: {PAYPAL_MAIL} (PayPal)
Die Bestellübersicht findest du im Anhang.
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = PAYPAL_MAIL
    msg["To"] = ", ".join([email_recipient, PAYPAL_MAIL])
    msg.set_content(body)
    msg.add_attachment(output.read(), maintype="application",
                       subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       filename="Bestellung.xlsx")

    gmail_user = PAYPAL_MAIL
    gmail_password = os.environ.get("GMAIL_PASSWORD")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_password)
        server.send_message(msg)

    return f"✅ Bestellung erfolgreich gesendet an {email_recipient}!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
