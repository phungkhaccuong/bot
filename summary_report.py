import os
import time

from dotenv import load_dotenv

from constants import sn10_hotkeys, cold_keys, sn28_hotkeys, sn5_hotkeys,sn16_hotkeys, sn25_hotkeys
from functions import send_miner_report, get_keys_rank_under_50

load_dotenv()

my_netuids = [10, 23, 28, 16, 25]

# tele_chat_id = os.getenv("TELE_CHAT_ID_V1")
# tele_report_token = os.getenv("TELE_REPORT_TOKEN_V1")
tele_chat_id = '1205550456'
tele_report_token = '6768286803:AAEOT-8Auf2FQWlApf5pyrl81G_g0x90gwU'

reward_map = {}

def main():
    hotkeys = {**sn10_hotkeys, **sn28_hotkeys, **sn5_hotkeys, **sn16_hotkeys, **sn25_hotkeys}
    while True:
        get_keys_rank_under_50(my_netuids, cold_keys, tele_chat_id,tele_report_token, reward_map, hotkeys)
        time.sleep(60*60)


if __name__ == "__main__":
    main()