import os
import time

import bittensor as bt
from dotenv import load_dotenv

from constants import sn28_cold_keys as cold_keys
from functions import send_balance_report

load_dotenv()

total_map = {}

tele_chat_id = os.getenv("TELE_CHAT_ID")
tele_report_token = os.getenv("TELE_REPORT_TOKEN")

if __name__ == "__main__":
    subtensor = bt.subtensor()
    while True:
        send_balance_report(subtensor, cold_keys, total_map, tele_chat_id,
                            tele_report_token)
        time.sleep(600)
