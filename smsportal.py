import logging
import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

def _resolve_log_path() -> str:
    """Return a writable path for the log file.
    Preference order:
    1) Same directory as the executable (when frozen) or script.
    2) %LOCALAPPDATA%/smsportal/smsportal.log (or %APPDATA% / home).
    """
    candidates = []
    try:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(base_dir, 'smsportal.log'))
    except Exception:
        pass

    appdata = os.getenv('LOCALAPPDATA') or os.getenv('APPDATA') or os.path.expanduser('~')
    if appdata:
        candidates.append(os.path.join(appdata, 'smsportal', 'smsportal.log'))

    for path in candidates:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            # Touch the file to confirm writability
            with open(path, 'a', encoding='utf-8'):
                pass
            return path
        except Exception:
            continue
    return 'smsportal.log'

if __name__ == "__main__":
    LOG_PATH = _resolve_log_path()
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting smsportal; logging to %s", LOG_PATH)

    # Read credentials from environment variables
    apiKey = os.getenv('SMSPORTAL_API_KEY')
    apiSecret = os.getenv('SMSPORTAL_API_SECRET')

    if not apiKey or not apiSecret:
        logger.error("Missing SMSPORTAL_API_KEY or SMSPORTAL_API_SECRET environment variables.")
        sys.exit(1)

    basic = HTTPBasicAuth(apiKey, apiSecret)
    message = "This is a test message from smsportal at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cellphone1 = "264816011868" #"27825720582" #"35699782805"
    cellphone2 = "35699782805"
    sendRequest = {"messages": [{"content": message, "destination": cellphone1, "customerId": "optimax_test_2"},
                                {"content": message, "destination": cellphone2, "customerId": "optimax_test_2"}
                                ]}

    try:
        sendResponse = requests.post(
            "https://rest.smsportal.com/bulkmessages",
            auth=basic,
            json=sendRequest
        )

        # Try to parse JSON, fall back to raw text for logging
        try:
            response_body = sendResponse.json()
        except Exception:
            response_body = sendResponse.text

        if sendResponse.status_code == 200:
            logger.info("Success: %s", response_body)
        else:
            logger.error("Failure (%s): %s", sendResponse.status_code, response_body)
    except Exception:
        logger.exception("Exception occurred during sending request.")
