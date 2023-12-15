import RPi.GPIO as GPIO
import time
import flask_cors
import flask
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = flask.Flask(__name__)
flask_cors.CORS(app)


def load_config() -> None:
    """Load the config file into the config variable."""
    global config
    with open('config.json') as json_file:
        config = json.load(json_file)

config = {}
load_config()

@app.before_request
def before_request() -> None:
    """Reload the config file before each request."""
    logger.debug("Reloading config")
    load_config()

@app.route('/', methods=['GET'])
def index() -> str:
    """Display hello world"""
    return "Hello World!"

@app.route('/power', methods=['POST'])
def power() -> str:
    """Send command to activate the relay."""
    if flask.request.method == 'POST':
        # get data if set
        data = flask.request.get_json()
        activate_relay(data.get('relay_time', None))
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


def activate_relay(time_on: float) -> None:
    """Activate the relay for the given time."""
    if time_on is None:
        time_on = 0.1
    logger.info(f"Activating relay for {time_on} seconds.")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config["relay_chan"], GPIO.OUT)
    try:
        GPIO.output(config["relay_chan"], GPIO.HIGH)
        time.sleep(time_on)
        GPIO.output(config["relay_chan"], GPIO.LOW)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Error activating relay: {e}")
    finally:
        GPIO.cleanup()
