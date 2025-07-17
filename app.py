# In deiner app.py im submit():
msg["Subject"] = f"Nudelbestellung von {name}"
msg["From"] = "opasnudelbusiness@gmail.com"
msg["To"] = ", ".join([email_recipient, "opasnudelbusiness@gmail.com"])

body = f"""Hallo {name},

vielen Dank für deine Bestellung! Hier die Übersicht:

Gesamtanzahl: {total_qty} Packungen
Gratis-Packungen: {free_packs}
Endpreis: {total_price:.2f} €

Bitte den Betrag an PayPal: opasnudelbusiness@gmail.com senden.

Anbei die Bestellübersicht als Excel-Datei.

Liebe Grüße
Opa Nudelbusiness 🍝
"""

# Spaltenbreite anpassen
ws.column_dimensions['A'].width = 40  # Erste Spalte breiter machen
