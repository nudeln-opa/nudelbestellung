<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Nudelbestellung</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #fafafa;
            color: #333;
        }
        h1 {
            color: #d35400;
            text-align: center;
        }
        h3 {
            text-align: center;
            color: #666;
            font-weight: normal;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
        }
        th {
            background: #f39c12;
            color: white;
        }
        img {
            width: 50px;
            height: auto;
            border-radius: 5px;
        }
        .summary {
            margin-top: 20px;
            font-size: 16px;
        }
        .summary b {
            color: #e67e22;
        }
        .form-section {
            margin-top: 20px;
        }
        input[type="text"], input[type="email"], select {
            padding: 8px;
            width: calc(100% - 20px);
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        input[type="number"] {
            width: 60px;
            text-align: center;
        }
        button {
            background: #e67e22;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background: #d35400;
        }
    </style>
</head>
<body>
    <h1>🍝 Nudelbestellung</h1>
    <h3>Nudeln wie zu Omas Zeiten – Ohne Geschmacksverstärker und Aromen</h3>

    <form id="orderForm" method="POST" action="/submit">
        <div class="form-section">
            <label>Name:</label>
            <input type="text" name="name" required>
            <label>Email:</label>
            <input type="email" name="email" required>
        </div>

        <table>
            <tr>
                <th>Nudel (500g)</th>
                <th>Bild</th>
                <th>Preis (€)</th>
                <th>Menge</th>
            </tr>
            {% for noodle in noodles %}
            <tr>
                <td>{{ noodle }}</td>
                <td><img src="{{ url_for('static', filename='images/' + noodle.replace(' ', '_') + '.JPG') }}" alt="{{ noodle }}"></td>
                <td>2.5</td>
                <td><input type="number" name="qty_{{ loop.index }}" value="0" min="0" onchange="updateSummary()"></td>
            </tr>
            {% endfor %}
        </table>

        <div class="summary">
            <p><b>Gesamtanzahl:</b> <span id="totalQty">0</span> Packungen</p>
            <p><b>Gratis-Packungen:</b> <span id="freePacks">0</span></p>
            <p><b>Zu zahlen:</b> <span id="totalPrice">0.00</span> €</p>
        </div>

        <div class="form-section">
            <label>Bezahlmethode:</label>
            <select name="payment_method">
                <option value="Bar">Bar</option>
                <option value="PayPal">PayPal</option>
            </select>
        </div>

        <button type="submit">Bestellen</button>
    </form>

    <script>
        const pricePerPack = 2.5;
        function updateSummary() {
            let totalQty = 0;
            document.querySelectorAll('input[type="number"]').forEach(input => {
                totalQty += parseInt(input.value || 0);
            });
            let freePacks = Math.floor(totalQty / 10);
            let totalPrice = totalQty * pricePerPack - freePacks * pricePerPack;
            document.getElementById('totalQty').textContent = totalQty;
            document.getElementById('freePacks').textContent = freePacks;
            document.getElementById('totalPrice').textContent = totalPrice.toFixed(2);
        }
    </script>
</body>
</html>
