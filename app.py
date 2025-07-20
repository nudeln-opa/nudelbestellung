from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Lade alle Bilddateien aus dem static-Ordner
    images = sorted(os.listdir('static'))

    # Filtere die Bilder nach Sorten
    hartweizen = [img for img in images if not img.lower().startswith('dinkel')]
    dinkel = [img for img in images if img.lower().startswith('dinkel')]

    return render_template('index.html', hartweizen=hartweizen, dinkel=dinkel)

@app.route('/bestellen', methods=['POST'])
def bestellen():
    name = request.form.get('name')
    email = request.form.get('email')
    zahlung = request.form.get('zahlung')

    bestellung = []
    gesamtmenge = 0
    gesamtpreis = 0.0

    # Alle Bilder durchgehen, um Mengen abzufragen
    images = sorted(os.listdir('static'))
    for img in images:
        menge = int(request.form.get(f'qty_{img}', 0))
        if menge > 0:
            preis = 2.80 if img.lower().startswith('dinkel') else 2.50
            gesamtpreis += menge * preis
            gesamtmenge += menge
            bestellung.append({
                'name': img.split('.')[0].replace('_', ' '),
                'menge': menge,
                'preis': preis
            })

    return render_template(
        'bestaetigung.html',
        name=name,
        email=email,
        zahlung=zahlung,
        bestellung=bestellung,
        gesamtmenge=gesamtmenge,
        gesamtpreis=gesamtpreis
    )

if __name__ == '__main__':
    app.run(debug=True)
