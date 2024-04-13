import os
import time

import bittensor as bt
import requests
from dotenv import load_dotenv
from prettytable import PrettyTable

from constants import sn5_cold_keys as cold_keys

load_dotenv()

total_map = {}

tele_chat_id = os.getenv("TELE_CHAT_ID")
tele_report_token = os.getenv("TELE_REPORT_TOKEN")


def main(subtensor):
    table = PrettyTable()
    table.field_names = ["NAME", "FREE", "STAKED", "TOTAL"]

    coldkeys = list(cold_keys.keys())
    wallet_names = list(cold_keys.values())

    free_balances = [
        subtensor.get_balance(coldkeys[i]) for i in range(len(coldkeys))
    ]
    staked_balances = [
        subtensor.get_total_stake_for_coldkey(coldkeys[i])
        for i in range(len(coldkeys))
    ]

    balances = {
        name: (coldkey, free, staked)
        for name, coldkey, free, staked in sorted(
            zip(wallet_names, coldkeys, free_balances, staked_balances)
        )
    }

    total_free_balance = sum(free_balances)
    total_staked_balance = sum(staked_balances)

    has_change = False
    for name, (coldkey, free, staked) in balances.items():
        total = free + staked

        arrow = ''
        if coldkey in total_map:
            if total_map[coldkey] > total:
                arrow = '↓'
                has_change = True
            elif total_map[coldkey] < total:
                arrow = '↑'
                has_change = True
        else:
            has_change = True

        table.add_row([
            name,
            str(free),
            str(staked),
            str(total) + arrow
        ])

        total_map[coldkey] = total
    table.add_row(["-", "-", "-", "-"])
    table.add_row([
        "All",
        str(total_free_balance),
        str(total_staked_balance),
        str(total_free_balance + total_staked_balance),
    ])

    if has_change:
        data = {
            "chat_id": tele_chat_id,
            "text": f'<pre>{table.get_string()}</pre>',
            "parse_mode": "HTML"
        }

        requests.post(
            f'https://api.telegram.org/bot{tele_report_token}/sendMessage',
            json=data)


if __name__ == "__main__":
    subtensor = bt.subtensor()
    while True:
        main(subtensor)
        time.sleep(600)
