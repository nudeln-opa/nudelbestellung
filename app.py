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

@app.route("/")
def index():
    paypal_info = "PayPal: opasnudelbusiness@gmail.com"
    return render_template("index.html", noodles=noodles, paypal=paypal_info)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    email_recipient = request.form["email"]

    # Mengen sammeln
    qtys = [int(request.form.get(f"qty_{i}", 0)) for i in range(1, len(noodles)+1)]
    total_qty = sum(qtys)

    # Gratis-Packungen: 1 pro 10 Stück
    free_packs = total_qty // 10
    price_per_pack = 2.5
    total_price = (total_qty - free_packs) * price_per_pack

    # Excel erstellen
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bestellung"

    # Spalte A breiter machen
    ws.column_dimensions['A'].width = 40

    ws.append(["Nudelsorte", "Preis (€)", "Menge", "Summe (€)"])
    for noodle, qty in zip(noodles, qtys):
        if qty > 0:
            ws.append([noodle, price_per_pack, qty, qty * price_per_pack])
    ws.append([])
    ws.append(["Gesamtanzahl", total_qty])
    ws.append(["Gratis-Packungen", free_packs])
    ws.append(["Endpreis (€)", total_price])

    # Excel in Speicher schreiben
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    paypal_info = "opasnudelbusiness@gmail.com"

    # E-Mail Inhalt
    subject = f"Nudelbestellung von {name}"
    body = f"""Hallo {name},

Danke für deine Bestellung!

Gesamtanzahl: {total_qty} Packungen
Gratis-Packungen: {free_packs}
Endpreis: {total_price:.2f} €

Bitte bezahle den Betrag per PayPal an:
➡ {paypal_info}

Anbei findest du die Bestellübersicht als Excel.
"""

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

    # Login-Daten
    gmail_user = "opasnudelbusiness@gmail.com"
    gmail_password = os.environ.get("GMAIL_PASSWORD")

    # Debug-Ausgabe
    print("=== DEBUG START ===")
    print("Gmail User:", gmail_user)
    print("Passwort Länge:", len(gmail_password) if gmail_password else "NICHT GESETZT")
    print("=== DEBUG END ===")

    # Mail senden
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_password)
        server.send_message(msg)

    return f"✅ Bestellung erfolgreich gesendet an {email_recipient} und Opa Nudelbusiness!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
