import json
import logging
import time

import flask
import flask_cors
import RPi.GPIO as GPIO
import asyncio
import telegram
import os

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler("power_button.log")
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

app = flask.Flask(__name__)
flask_cors.CORS(app)

RELAY_CHAN = 21

bot = telegram.Bot(os.environ.get("TELEGRAM_TOKEN"))


@app.route("/", methods=["GET"])
def index():
    """Display hello world."""
    return "Hello World!"


@app.route("/power", methods=["POST"])
def power():
    """Send command to activate the relay."""
    data = flask.request.get_json(force=True, silent=True) or {}
    activate_relay(data.get("relay_time", 0.1))
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


async def send_message(text):
    async with bot:
        await bot.send_message(text=text, chat_id=os.environ.get("TELEGRAM_CHAT_ID"))


def activate_relay(time_on: float):
    """Activate the relay for the given time."""
    logger.info(f"rasPMI: Activating relay for {time_on} seconds.")
    asyncio.run(send_message(f"rasPMI: Pressing power button for {time_on} seconds."))
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_CHAN, GPIO.OUT)
    try:
        GPIO.output(RELAY_CHAN, GPIO.HIGH)
        time.sleep(time_on)
        GPIO.output(RELAY_CHAN, GPIO.LOW)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Error activating relay: {e}")
        asyncio.run(send_message(f"rasPMI: Error activating relay: {e}"))
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
