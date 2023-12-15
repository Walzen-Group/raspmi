import json
import logging
import time

import flask
import flask_cors
import RPi.GPIO as GPIO

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('power_button.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

app = flask.Flask(__name__)
flask_cors.CORS(app)

config = {}

def load_config():
    """Load the config file into the config variable."""
    global config
    try:
        with open('config.json') as json_file:
            config = json.load(json_file)
    except Exception as e:
        logger.error(f"Error loading config: {e}")

load_config()

@app.before_request
def before_request():
    """Reload the config file before each request."""
    logger.debug("Reloading config")
    load_config()

@app.route('/', methods=['GET'])
def index():
    """Display hello world."""
    return "Hello World!"

@app.route('/power', methods=['POST'])
def power():
    """Send command to activate the relay."""
    data = flask.request.get_json()
    activate_relay(data.get('relay_time', 0.1))
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

def activate_relay(time_on: float):
    """Activate the relay for the given time."""
    logger.info(f"Activating relay for {time_on} seconds.")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.get("relay_chan", 21), GPIO.OUT)
    try:
        GPIO.output(config.get("relay_chan", 21), GPIO.HIGH)
        time.sleep(time_on)
        GPIO.output(config.get("relay_chan", 21), GPIO.LOW)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Error activating relay: {e}")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
