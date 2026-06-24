from flask import Flask, render_template, request, jsonify
import os, requests

app = Flask(__name__)

RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@byjeremiahsmith.ink')
TO_EMAIL = 'jeremiah@creativekonsoles.com'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contact', methods=['POST'])
def contact():
    data = request.json or {}
    name = data.get('name', '').strip()[:100]
    email = data.get('email', '').strip()[:100]
    interest = data.get('interest', '').strip()[:100]
    message = data.get('message', '').strip()[:2000]

    if not name or not email or not message:
        return jsonify({'ok': False, 'error': 'All fields required'}), 400

    interest_line = f'<p><strong>Interested in:</strong> {interest}</p>' if interest else ''

    if RESEND_API_KEY:
        try:
            r = requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {RESEND_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'from': FROM_EMAIL,
                    'to': [TO_EMAIL],
                    'subject': f'Portfolio contact from {name}',
                    'html': f'<p><strong>Name:</strong> {name}</p><p><strong>Email:</strong> {email}</p>{interest_line}<p><strong>Message:</strong><br>{message.replace(chr(10), "<br>")}</p>'
                },
                timeout=10
            )
            if r.status_code in (200, 201):
                return jsonify({'ok': True})
        except Exception:
            pass

    return jsonify({'ok': True})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5576))
    host = '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
    app.run(host=host, port=port, debug=not os.environ.get('PORT'))
