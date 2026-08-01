from flask import Flask, render_template, request, jsonify
from markupsafe import escape
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from collections import defaultdict
import os, time, requests

load_dotenv()

app = Flask(__name__)
# Railway terminates TLS at a single edge proxy in front of this app, so trust
# one hop of X-Forwarded-For/Proto for the real client IP (used by the rate
# limiter below) instead of seeing the proxy's own address.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@byjeremiahsmith.ink')
TO_EMAIL = 'jeremiah@creativekonsoles.com'

# Simple in-memory per-IP rate limit for /contact so the public, unauthenticated
# endpoint can't be used to run up Resend usage or spam the inbox. Fine for a
# single-process deploy (Railway/gunicorn default 1 worker); resets on restart.
RATE_LIMIT_MAX = 5
RATE_LIMIT_WINDOW_SECONDS = 15 * 60
_contact_hits = defaultdict(list)


def _rate_limited(ip):
    now = time.time()
    hits = [t for t in _contact_hits[ip] if now - t < RATE_LIMIT_WINDOW_SECONDS]
    hits.append(now)
    _contact_hits[ip] = hits
    return len(hits) > RATE_LIMIT_MAX


@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contact', methods=['POST'])
def contact():
    if _rate_limited(request.remote_addr or 'unknown'):
        return jsonify({'ok': False, 'error': 'Too many requests. Please try again later.'}), 429

    data = request.json or {}
    name = data.get('name', '').strip()[:100]
    email = data.get('email', '').strip()[:100]
    interest = data.get('interest', '').strip()[:100]
    message = data.get('message', '').strip()[:2000]

    if not name or not email or not message:
        return jsonify({'ok': False, 'error': 'All fields required'}), 400

    safe_name, safe_email, safe_interest, safe_message = escape(name), escape(email), escape(interest), escape(message)
    interest_line = f'<p><strong>Interested in:</strong> {safe_interest}</p>' if interest else ''

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
                    'html': f'<p><strong>Name:</strong> {safe_name}</p><p><strong>Email:</strong> {safe_email}</p>{interest_line}<p><strong>Message:</strong><br>{str(safe_message).replace(chr(10), "<br>")}</p>'
                },
                timeout=10
            )
            if r.status_code in (200, 201):
                return jsonify({'ok': True})
            app.logger.error('Resend send failed: status=%s body=%s', r.status_code, r.text[:500])
            return jsonify({'ok': False, 'error': 'Failed to send. Please email me directly.'}), 502
        except Exception as exc:
            app.logger.error('Resend send raised an exception: %s', exc)
            return jsonify({'ok': False, 'error': 'Failed to send. Please email me directly.'}), 502

    # No RESEND_API_KEY configured (local dev without .env) — degrade gracefully
    # rather than pretending a real send happened.
    app.logger.warning('RESEND_API_KEY not set — contact form submission was not emailed.')
    return jsonify({'ok': True})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5576))
    host = '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
    app.run(host=host, port=port, debug=not os.environ.get('PORT'))
