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
    department = request.form["department"]
    email_recipient = request.form["email"]
    qtys = [int(request.form.get(f"qty_{i}", 0)) for i in range(1, len(noodles)+1)]
    total_qty = sum(qtys)
    free_packs = 0
    if total_qty > 50: free_packs = 5
    elif total_qty > 40: free_packs = 4
    elif total_qty > 30: free_packs = 3
    elif total_qty > 20: free_packs = 2
    elif total_qty > 10: free_packs = 1
    price_per_pack = 2.5
    total_price = total_qty * price_per_pack - free_packs * price_per_pack

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bestellung"
    ws.append(["Nudelsorte", "Preis (€)", "Menge", "Summe (€)"])
    for noodle, qty in zip(noodles, qtys):
        if qty > 0:
            ws.append([noodle, price_per_pack, qty, qty * price_per_pack])
    ws.append([])
    ws.append(["Gesamtanzahl", total_qty])
    ws.append(["Gratis-Packungen", free_packs])
    ws.append(["Endpreis (€)", total_price])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    subject = f"Nudelbestellung von {name} ({department})"
    body = f"""Danke für deine Bestellung, {name} aus {department}.

Gesamtanzahl: {total_qty} Packungen
Gratis-Packungen: {free_packs}
Endpreis: {total_price:.2f} €

Anbei die Bestellübersicht.
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "opasnudelbusiness@gmail.com"   # HIER: muss mit App-Passwort übereinstimmen
    msg["To"] = ", ".join([email_recipient, "opasnudelbusiness@gmail.com"])
    msg.set_content(body)
    msg.add_attachment(output.read(), maintype="application",
                       subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       filename="Bestellung.xlsx")

    gmail_user = "opasnudelbusiness@gmail.com"  # HIER: muss exakt der Account sein
    gmail_password = os.environ.get("GMAIL_PASSWORD")

    # ✅ Debug-Ausgaben
    print("=== DEBUG START ===")
    print("Gmail User:", gmail_user)
    print("Passwort Länge:", len(gmail_password) if gmail_password else "NICHT GESETZT")
    print("=== DEBUG END ===")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_password)
        server.send_message(msg)

    return f"✅ Bestellung erfolgreich gesendet an {email_recipient} und Opa Nudelbusiness!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

