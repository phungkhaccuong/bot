import os
import time

from dotenv import load_dotenv

from constants import sn10_hotkeys as hotkeys, cold_keys
from functions import send_miner_report

load_dotenv()

my_netuids = [10]

# tele_chat_id = '-4151737386'
# tele_report_token = '6408369939:AAHKfnIxyihyXoJ3p1WNN2cgaSD4ielBJtw'

tele_report_token = '6768286803:AAEOT-8Auf2FQWlApf5pyrl81G_g0x90gwU'
tele_chat_id = '1205550456'

reward_map = {}

def main():
    while True:
        send_miner_report(my_netuids, cold_keys, tele_chat_id,
                          tele_report_token,
                          reward_map, hotkeys)
        time.sleep(300)


if __name__ == "__main__":
    main()
