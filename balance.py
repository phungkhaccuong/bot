import os
import time

import bittensor as bt
from dotenv import load_dotenv

from constants import cold_keys
from functions import send_balance_report

load_dotenv()

total_map = {}

# tele_chat_id = os.getenv("TELE_CHAT_ID_V1")
# tele_report_token = os.getenv("TELE_REPORT_TOKEN_V1")
tele_chat_id = '1205550456'
tele_report_token = '6768286803:AAEOT-8Auf2FQWlApf5pyrl81G_g0x90gwU'

if __name__ == "__main__":
    subtensor = bt.subtensor()
    while True:
        send_balance_report(subtensor, cold_keys, total_map, tele_chat_id,
                            tele_report_token)
        time.sleep(60*60)
