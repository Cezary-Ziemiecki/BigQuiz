import sys
from app.app import app
import signal
from constants import FLASK_PORT


def signal_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=5500, debug=False, ssl_context=('cert.pem', 'key.pem'))
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=False)
