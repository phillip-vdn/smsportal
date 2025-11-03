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
    apiKey = smsportal_api_key
    apiSecret = smsportal_api_secret

    LOG_PATH = _resolve_log_path()
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting smsportal; logging to %s", LOG_PATH)

    basic = HTTPBasicAuth(apiKey, apiSecret)
    message = "This is a test message from smsportal at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cellphone = "35699782805"
    sendRequest = {"messages": [{"content": message, "destination": cellphone, "customerId": "optimax_test_2"},
                                ]}

    # sendRequest = {"messages": [{"content": "MS E TEST FLASH SALE! 10 - 19 July!! 20 PERCENT off selected frames. Book now 0819542400 or 2401", "destination": "0825720582"},
    #                 {"content": "BLACK NOVEMBER! 20%30%50% DISCOUNT FOR EVERY FAMILY MEMBER. CALL FOR APPOINTMENT 061 000000", "destination": "0825720582"},
    #                 {"content": "Testing sms portal message", "destination": "0825720582"},
    #                 {"content": "MS E TEST FLASH SALE! 10 - 19 July!! 20 PERCENT off selected frames. Book now 0819542400 or 2401", "destination": "35699782805"},
    #                 {"content": "BLACK NOVEMBER! 20%30%50% DISCOUNT FOR EVERY FAMILY MEMBER. CALL FOR APPOINTMENT 061 000000", "destination": "35699782805"},
    #                 {"content": "Testing sms portal message", "destination": "35699782805"},
    #                 {"content": "MS E TEST FLASH SALE! 10 - 19 July!! 20 PERCENT off selected frames. Book now 0819542400 or 2401", "destination": "0832805061"},
    #                 {"content": "BLACK NOVEMBER! 20%30%50% DISCOUNT FOR EVERY FAMILY MEMBER. CALL FOR APPOINTMENT 061 000000", "destination": "0832805061"},
    #                 {"content": "Testing sms portal message", "destination": "0832805061"},
    #                 {"content": "MS E TEST FLASH SALE! 10 - 19 July!! 20 PERCENT off selected frames. Boo,k now 0819542400 or 2401", "destination": "0820423320"},
    #                 {"content": "BLACK NOVEMBER! 20%30%50% DISCOUNT FOR EVERY FAMILY MEMBER. CALL FOR APPOINTMENT 061 000000", "destination": "0820423320"},
    #                 {"content": "Testing sms portal message", "destination": "0820423320"},
    #                 {"content": "MS E TEST FLASH SALE! 10 - 19 July!! 20 PERCENT off selected frames. Book now 0819542400 or 2401", "destination": "0846934142"},
    #                 {"content": "BLACK NOVEMBER! 20%30%50% DISCOUNT FOR EVERY FAMILY MEMBER. CALL FOR APPOINTMENT 061 000000", "destination": "0846934142"},
    #                 {"content": "Testing sms portal message", "destination": "0846934142"}]}

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
