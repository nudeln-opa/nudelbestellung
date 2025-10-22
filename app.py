import os
from flask import Flask, render_template, request
import smtplib, ssl
from email.message import EmailMessage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# ✅ Finale Reihenfolge der Nudeln (Dateinamen bleiben gleich)
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

@app.route("/")
def index():
    return render_template("index.html", noodles=noodles)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "Unbekannt")
    email_recipient = request.form.get("email")
    payment_method = request.form.get("payment_method", "Bar")

    qtys = [int(request.form.get(f"qty_{i}", 0) or 0) for i in range(1, len(noodles)+1)]
    total_qty = sum(qtys)
    free_packs = total_qty // 10
    price_per_pack = 2.50
    total_price = total_qty * price_per_pack - free_packs * price_per_pack

    # ✅ HTML-Tabelle für die E-Mail – mit Leerzeichen vor "mm" und "%"
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
            # ✅ Anzeige optimieren → Leerzeichen einfügen
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

    # ✅ Email-Inhalt mit Gratis-Packungen & Leerzeichen bei mm/%
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

    # ✅ PayPal-Link nur falls gewählt
    if payment_method == "PayPal":
        body_html += "<p>Hier kannst du bequem per PayPal bezahlen: <a href='https://paypal.me/jscheel1712'>paypal.me/jscheel1712</a></p>"

    # ✅ Footer
    body_html += """
    <p>Für zukünftige Bestellungen besuche: 
    <a href='https://nudelbestellung.onrender.com'>nudelbestellung.onrender.com</a></p>
    <p>Nudelige Grüße,<br>Opa</p>
    """

    # ✅ Mail zusammenbauen
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "opasnudelbusiness@gmail.com"
    msg["To"] = ", ".join([email_recipient, "opasnudelbusiness@gmail.com"])
    msg.set_content("Bitte HTML-E-Mail aktivieren, um die Bestellung zu sehen.")
    msg.add_alternative(body_html, subtype="html")

# ✅ Mail asynchron versenden, um Render-Timeout zu vermeiden
def send_email_async(msg):
    import smtplib, ssl
    mailjet_user = os.environ.get("MAILJET_USER")
    mailjet_pass = os.environ.get("MAILJET_PASS")
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("in-v3.mailjet.com", 465, context=context) as server:
            server.login(mailjet_user, mailjet_pass)
            server.send_message(msg)
            print("✅ Mail erfolgreich gesendet.")
    except Exception as e:
        print("❌ Fehler beim E-Mail-Versand:", e)

# 🧵 Starte Hintergrund-Thread, damit Render nicht blockiert
threading.Thread(target=send_email_async, args=(msg,)).start()

    return f"✅ Bestellung erfolgreich gesendet an {email_recipient} und Opa!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
