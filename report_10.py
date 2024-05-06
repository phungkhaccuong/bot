import os
import time

from dotenv import load_dotenv

from constants import sn10_hotkeys as hotkeys, cold_keys
from functions import send_miner_report

load_dotenv()

my_netuids = [10]

tele_chat_id = os.getenv("TELE_CHAT_ID")
tele_report_token = os.getenv("TELE_REPORT_TOKEN")
tele_chat_id = "-4151737386"

def main():
    while True:
        send_miner_report(my_netuids, cold_keys, tele_chat_id,
                          tele_report_token,
                          reward_map, hotkeys)
        time.sleep(300)


if __name__ == "__main__":
    main()
