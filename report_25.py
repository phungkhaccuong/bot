import os
import time

from dotenv import load_dotenv

from constants import sn25_hotkeys as hotkeys, cold_keys
from functions import send_miner_report

load_dotenv()

my_netuids = [25]

tele_chat_id = os.getenv("TELE_CHAT_ID")
tele_report_token = os.getenv("TELE_REPORT_TOKEN")


reward_map = {}


def main():
    while True:
        send_miner_report(my_netuids, cold_keys, tele_chat_id,
                          tele_report_token,
                          reward_map, hotkeys)
        time.sleep(300)


if __name__ == "__main__":
    main()
