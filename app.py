import os
from flask import Flask, render_template, request
import smtplib, ssl, io
from email.message import EmailMessage
import openpyxl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
app = Flask(__name__, template_folder=TEMPLATE_DIR)

noodles = [
    "Hartweizennudeln 6mm 30% Vollkorn 500g",
    "Casarecce 500g",
    "Wellenspätzle 500g",
    "Bandnudeln 9,5 mm 500g",
    "Bandnudeln 6 mm 500g",
    "Wellenbandnudeln 500g",
    "Campanelle 500g",
    "Spiralnudeln 500g",
    "Spaghetti 500g",
    "Suppennudeln 500g",
    "Dinkelnudeln 6mm 30% Vollkorn 500g",
    "Dinkelcasarecce 500g",
    "Dinkelspätzle 500g",
    "Dinkelwellenspätzle 500g",
    "Dinkelbandnudeln 9,5 mm 500g",
    "Dinkelbandnudeln 6 mm 500g",
    "Dinkelwellenbandnudeln 500g",
    "Dinkelcampanelle 500g",
    "Dinkelspiralnudeln 500g",
    "Dinkelspaghetti 500g",
    "Dinkelsuppennudeln 500g"
]

PRICE_PER_PACK = 2.5
PAYPAL_INFO = "PayPal: opasnudelbusiness@gmail.com"

@app.route("/")
def index():
    return render_template("index.html", noodles=noodles, price_per_pack=PRICE_PER_PACK, paypal=PAYPAL_INFO)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    email_recipient = request.form["email"]

    # Mengen aus Formular lesen
    qtys = [int(request.form.get(f"qty_{i}", 0)) for i in range(1, len(noodles)+1)]
    total_qty = sum(qtys)
    free_packs = total_qty // 10  # Jede 10. gratis
    total_price = total_qty * PRICE_PER_PACK - free_packs * PRICE_PER_PACK

    # Excel erstellen
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bestellung"
    ws.column_dimensions['A'].width = 40
    ws.append(["Nudelsorte", "Preis (€)", "Menge", "Summe (€)"])
    for noodle, qty in zip(noodles, qtys):
        if qty > 0:
            ws.append([noodle, PRICE_PER_PACK, qty, qty * PRICE_PER_PACK])
    ws.append([])
    ws.append(["Gesamtanzahl", total_qty])
    ws.append(["Gratis-Packungen", free_packs])
    ws.append(["Endpreis (€)", total_price])

    # Excel in Memory speichern
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # Email-Inhalt
    subject = f"Nudelbestellung von {name}"
    body = (
        f"Hallo {name},\n\n"
        f"danke für deine Bestellung!\n\n"
        f"Gesamtanzahl: {total_qty} Packungen\n"
        f"Gratis-Packungen: {free_packs}\n"
        f"Endpreis: {total_price:.2f} €\n\n"
        f"Bitte bezahle per PayPal an: {PAYPAL_INFO}\n\n"
        f"Die Bestellübersicht ist im Anhang als Excel-Datei.\n"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "opasnudelbusiness@gmail.com"
    msg["To"] = ", ".join([email_recipient, "opasnudelbusiness@gmail.com"])
    msg.set_content(body)
    msg.add_attachment(
        output.read(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="Bestellung.xlsx"
    )

    # SMTP Login
    gmail_user = "opasnudelbusiness@gmail.com"
    gmail_password = os.environ.get("GMAIL_PASSWORD")

    print("=== DEBUG ===")
    print("Gmail User:", gmail_user)
    print("Passwort gesetzt:", bool(gmail_password))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_password)
        server.send_message(msg)

    return f"✅ Bestellung erfolgreich gesendet an {email_recipient} und Opa Nudelbusiness!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
