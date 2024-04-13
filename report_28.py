import requests
import time
from io import StringIO
from prettytable import PrettyTable
import pandas as pd

import os
from dotenv import load_dotenv

load_dotenv()

burn_map = {}
my_netuids = [28]

tele_chat_id = '-4055355950'
tele_report_token = os.getenv("TELE_REPORT_TOKEN")
reward_map = {}

cold_keys = [
    '5HdG2X4Xrbiw5C752yzqraVmSZhTWptkVMCZRwo8gMzppFPi',
    '5D7nqA4MwzHHksK8FHwiB4Z4WBzusKDUcBCWWZ8rQbqj2oym',
    '5HeYXUnv3sGPV43ariRoqZhMonuE5H37qQnP5ro7qdoF7xp1'
]
hotkeys = {
    '5CPgFFmjEnFSnV7qFkDvHXxUEmT7XjFWEz829ymFekADqyaX': 'wl1.hk1',
    '5EAYBsnJgGpTXm3PQmLGJ9MZS5QCLc1PA1yTFvBQSZZ4aD51': 'wl1.hk2',
    '5Dho8f9xkYV3om7ZVU7bVFWfe3pJDscActg4nC3uCPqFwZcc': 'wl1.hk3',
    '5HmJhpvp8tf6CiCRFmsAw8ZHacogAMvXrW85xU5mNsP9NELb': 'wl1.hk4',
    '5CMH6e5VagDNJxeR7U94GbPLqnXEdhzb61imdrZ1HPRsrX2j': 'wl1.hk5',

    '5E78VfZrZG8jufU3HLXXS6MVPUvWkgHP2CTYiopwAgUEvggG': 'wl2.hk1',
    '5Fc7tiFSpPbNxaLiK3RM5d7i12af5U3yq4Pufix9nZjt2Ykz': 'wl2.hk2',
    '5DceT6g9hjEpCNFQfVavjC6KJYyvkPajyHsyqismmRBfNkpT': 'wl2.hk3',
    '5Dh8vYkGe74JgbDhqYDdXmieknJxnoGXDfENAhtUTPen7XaG': 'wl2.hk4',
    '5FdzYMaXpPKxVDoEkZoF3DZKRFYC3n9Vnux2GD3YLJ8PTLHi': 'wl2.hk5',

    '5HThjQQR8ysi6u8drthhUHKn76HEAFMm4KJBymS2stojjBgY': 'wl3.hk1',
    '5HVtCiyTu47e4fSwvomPr8rv9HFbHqXP8NoWTVMQ7ENbuwxz': 'wl3.hk2',
    '5H3bSpMkSBe5b2UdvMv4qqpgPikCeGr1a2vtszC7q7PcApSr': 'wl3.hk3',
    '5EZPMgiZCDz8z4u71yQPwTguxVNrvr2HDHsUDP3c2oaV6etC': 'wl3.hk4',
    '5G6XDon6bDxdFHtd3dBzTcMUAsu8EaMpDmfnKEZU3hAfo5Md': 'wl3.hk5'
}


def get_subnet_reward(netuid, cold_keys, rewards):
    x = PrettyTable()
    x.field_names = ["STT", "UID", "HOT", "INCENTIVE", "REWARDS", "RANK"]
    url = 'https://taostats.io/wp-admin/admin-ajax.php'
    data = {
        'action': 'metagraph_table',
        'this_netuid': netuid
    }

    response = requests.post(url, data=data)

    tables = pd.read_html(StringIO(response.text))
    df = tables[0].sort_values(by='INCENTIVE', ascending=True)
    incentives = df['INCENTIVE']

    has_change = False
    df = df[df['COLDKEY'].isin(cold_keys)]
    if df.empty:
        return '', has_change

    incentives = incentives[incentives > 0]

    i = 0
    for index, row in df.iterrows():
        key = f'{netuid}_{row["UID"]}'
        arrow = ''
        if key in reward_map:
            if reward_map[key] > row['DAILY REWARDS']:
                arrow = '↓'
                has_change = True
            elif reward_map[key] < row['DAILY REWARDS']:
                arrow = '↑'
                has_change = True
        else:
            has_change = True

        i += 1
        reward_map[key] = row['DAILY REWARDS']
        hot_name = hotkeys.get(row['HOTKEY'], '')
        x.add_row([i, row['UID'], hot_name, row['INCENTIVE'],
                   '{0:.3f}'.format(row['DAILY REWARDS']) + arrow,
                   incentives[incentives < row['INCENTIVE']].count() + 1])
        rewards.append(row['DAILY REWARDS'])

    return x.get_string(), has_change


def send_report():
    text = ''
    rewards = []
    need_send = False
    for netuid in my_netuids:
        string, has_change = get_subnet_reward(netuid, cold_keys, rewards)
        if has_change:
            need_send = True
        if string != '':
            text += f'\nNetuid: {netuid} <pre>{string}</pre>'
    text += f'\nTotal: {sum(rewards)}'

    if not need_send:
        return

    data = {
        "chat_id": tele_chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    requests.post(
        f'https://api.telegram.org/bot{tele_report_token}/sendMessage',
        json=data)


def main():
    while True:
        send_report()
        time.sleep(300)


if __name__ == "__main__":
    main()
