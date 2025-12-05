import os
from flask import Flask, render_template, request
import requests
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Finale Reihenfolge der Nudeln (Dateinamen bleiben gleich)
noodles = [
    "Bandnudeln 6mm 30% Vollkorn",
    "Casarecce",
    "Wellenspätzle",
    "Bandnudeln 6mm",
    "Bandnudeln 9,5mm",
    "Wellenbandnudeln",
    "Campanelle",
    "Spiralnudeln",
    "Spaghetti",
    "Suppennudeln",
    "Dinkelbandnudeln 6mm 30% Vollkorn",
    "Dinkelcasarecce",
    "Dinkelspätzle",
    "Dinkelwellenspätzle",
    "Dinkelbandnudeln 6mm",
    "Dinkelbandnudeln 9,5mm",
    "Dinkelwellenbandnudeln",
    "Dinkelcampanelle",
    "Dinkelspiralnudeln",
    "Dinkelspaghetti",
    "Dinkelsuppennudeln"
]

# Mailjet Zugangsdaten aus Environment
MAILJET_API_KEY = os.environ.get("MAILJET_API_KEY")
MAILJET_API_SECRET = os.environ.get("MAILJET_API_SECRET")

# Fester Absender (nur im Code, NICHT als ENV nötig)
MAILJET_SENDER_EMAIL = "opasnudelbusiness@gmail.com"
MAILJET_SENDER_NAME = "Opas Nudelbusiness"


def send_email_mailjet(subject: str, body_html: str, recipients: list[str]):
    """
    E-Mail per Mailjet HTTP-API senden (HTTPS, daher auf Render Free erlaubt).
    """
    if not MAILJET_API_KEY or not MAILJET_API_SECRET:
        print("❌ MAILJET_API_KEY oder MAILJET_API_SECRET nicht gesetzt!")
        return

    url = "https://api.mailjet.com/v3.1/send"
    data = {
        "Messages": [
            {
                "From": {
                    "Email": MAILJET_SENDER_EMAIL,
                    "Name": MAILJET_SENDER_NAME,
                },
                "To": [{"Email": r} for r in recipients],
                "Subject": subject,
                "TextPart": "Bitte HTML-E-Mail aktivieren, um die Bestellung zu sehen.",
                "HTMLPart": body_html,
            }
        ]
    }

    try:
        print("📨 Versuche, Mail über Mailjet-API zu senden...")
        resp = requests.post(
            url,
            auth=(MAILJET_API_KEY, MAILJET_API_SECRET),
            json=data,
            timeout=10,
        )
        print("📬 Mailjet-Statuscode:", resp.status_code)
        print("📬 Mailjet-Antwort:", resp.text)
        resp.raise_for_status()
        print("✅ Mailjet: E-Mail erfolgreich gesendet.")
    except Exception as e:
        print("❌ Fehler beim E-Mail-Versand über Mailjet:", e)


def send_email_async(subject: str, body_html: str, recipients: list[str]):
    """Wrapper, um den Mailversand in einem eigenen Thread zu starten."""
    threading.Thread(
        target=send_email_mailjet,
        args=(subject, body_html, recipients),
        daemon=True,
    ).start()


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
    free_packs = total_qty // 10
    price_per_pack = 2.50
    total_price = total_qty * price_per_pack - free_packs * price_per_pack

    # HTML-Tabelle für die E-Mail mit Leerzeichen vor "mm" und "%"
    table_html = """
    <table border='1' cellspacing='0' cellpadding='5' style='border-collapse: collapse; width: 70%;'>
        <tr style='background:#f2f2f2;'>
            <th style='text-align:left;'>Nudel</th>
            <th>Menge</th>
            <th>Einzelpreis (€)</th>
            <th>Summe (€)</th>
        </tr>
    """
    for noodle, qty in zip(noodles, qtys):
        if qty > 0:
            display_name = noodle.replace("mm", " mm").replace("%", " %")
            table_html += f"""
            <tr>
                <td>{display_name}</td>
                <td style='text-align:center;'>{qty}</td>
                <td style='text-align:center;'>{price_per_pack:.2f}</td>
                <td style='text-align:right;'>{qty * price_per_pack:.2f}</td>
            </tr>
            """
    table_html += "</table>"

    subject = f"Nudelbestellung von {name}"
    body_html = f"""
    <p>Hallo {name},</p>
    <p>vielen Dank für deine Bestellung!</p>
    {table_html}
    <p>
    <b>Gesamtanzahl:</b> {total_qty} Packungen<br>
    <b>Gratis-Packungen:</b> {free_packs}<br>
    <b>Endpreis:</b> {total_price:.2f} €<br>
    <b>Bezahlmethode:</b> {payment_method}
    </p>
    """

    if payment_method == "PayPal":
        body_html += "<p>Hier kannst du bequem per PayPal bezahlen: <a href='https://paypal.me/jscheel1712'>paypal.me/jscheel1712</a></p>"

    body_html += """
    <p>Für zukünftige Bestellungen besuche: 
    <a href='https://nudelbestellung.onrender.com'>nudelbestellung.onrender.com</a></p>
    <p>Nudelige Grüße,<br>Opa</p>
    """

    # Empfänger: Besteller + Opa
    recipients = [addr for addr in [email_recipient, MAILJET_SENDER_EMAIL] if addr]

    # Asynchron senden
    send_email_async(subject, body_html, recipients)

    print(f"✅ Bestellung erfolgreich vorbereitet für {recipients}")

    return render_template(
    "index.html",
    noodles=noodles,
    message="✅ Bestellung erfolgreich gesendet."
)


if __name__ == "__main__":
    # Lokal testen
    app.run(host="0.0.0.0", port=5000, debug=True)
