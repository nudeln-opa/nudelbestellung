from flask import Flask, render_template, request
import smtplib
import ssl
from email.message import EmailMessage
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    department = request.form['department']
    order_details = request.form['order_details']
    user_email = request.form['email']

    # Gmail Konfiguration
    gmail_user = "opasnudelbusiness@gmail.com"
    gmail_password = os.environ.get("GMAIL_PASSWORD")

    # Debug-Ausgabe in Render Logs
    print("=== DEBUG START ===")
    print("Gmail User:", gmail_user)
    if gmail_password:
        print("Passwort Länge:", len(gmail_password))
        print("Passwort (erste 4 Zeichen):", gmail_password[:4], "...")
    else:
        print("!!! ACHTUNG: Kein Passwort gefunden !!!")
    print("=== DEBUG END ===")

    # E-Mail vorbereiten
    msg = EmailMessage()
    msg['Subject'] = f"Nudelbestellung von {name}"
    msg['From'] = gmail_user
    msg['To'] = [gmail_user, user_email]  # Besteller bekommt Kopie
    msg.set_content(f"Bestellung von {name} ({department}):\n\n{order_details}")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(gmail_user, gmail_password)  # <- hier kommt der Fehler
            server.send_message(msg)
        return "Bestellung erfolgreich gesendet!"
    except smtplib.SMTPAuthenticationError as e:
        return f"Authentifizierungsfehler: {e}"
    except Exception as e:
        return f"Fehler beim Senden: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
