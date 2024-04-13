import requests
import time
from io import StringIO
from prettytable import PrettyTable
import pandas as pd

import os
from dotenv import load_dotenv

load_dotenv()

burn_map = {}
my_netuids = [5]

tele_chat_id = os.getenv("TELE_CHAT_ID")
tele_report_token = os.getenv("TELE_REPORT_TOKEN")
reward_map = {}

cold_keys = {
    '5HU3TMzUSXxFmxBvmUN5Yf1qqxvfeebNXb625VhYDrex2q3i': 'ws501',
    '5CzDXfhh2dXCMrk5KJLecaQoiVXXjeGswtCTnT1PfLBARsXv': 'ws502',
    '5Fh6rCP6Cj2bsURiz1EGENseKcwmGUCpyQT15S6fcrxiEPJ8': 'ws503',
    '5FcKjwtX3qrNL8toxTqfyKtj6jNbUYYHrFWwBghhxsZ2iFmX': 'ws504',
}
hotkeys = {
    '5GRjd5FrshcP1LDF4ENc3CHS2kAde8v5PxstR6kLDkzYfonm': 'ws501.hk1',
    '5Fk1BFBscpM8kJxtxB5JGMF2TPqtjQuyP2dPMhEJtFCitXoV': 'ws501.hk2',
    '5CHuktrfPwCL9XXKmk88uZGzqAGgL8TJWmfK8BxPAZMUJ4V5': 'ws501.hk3',
    '5HL3NG6EQriU46LGVhQthsdofkKwzasDrnFcnpyQSkqhkyxo': 'ws501.hk4',
    '5G47KPN28FSWVxwxRVHEY5XXRzJksVFuEiinWbVDK3Yj71Gu': 'ws501.hk5',
    '5HEPFmnX8ofrBMxHWaZiyF1N9L8V3TWLrmXBQ8ong3x18iA6': 'ws501.hk6',
    '5GTYXsbs1ySaQF1tMeZnM7D7xnHTMenFj9gUjEFj6Ym6NDZU': 'ws501.hk7',
    '5Hmzrh9mYQhSfYG29RVKTWsg5PW7y43DS7WpBoES4V6xpjd4': 'ws501.hk8',
    '5CSFmFCCBDL1gVKkJRUTqwpAgA596MkNG5w2SQL7LGjvcaQu': 'ws501.hk9',
    '5F1HSrZ3kJ7GKzH5NFfJf1zqgyXuM5QamfgL1uBE5b3bHkV6': 'ws501.hk10',

    '5F2QETacAJsNxuPtBMSGHMS3GKgexfuNfbXpZTgfKfAtiWVJ': 'ws502.hk1',
    '5D2NbJrETr3vyKG7CGoU9Tzc4go6UoW9SPAHgLduu7mfhieo': 'ws502.hk2',
    '5HawLALUJ5hi7gyqTXjxVJqZ2UcBhVcnCdPRpa4Z8TuLdbQW': 'ws502.hk3',
    '5Hmrjqpyb2JuEmmvSAyhzsy36Qa5Cpk2QRH2VQ7Mc2QJX1Gx': 'ws502.hk4',
    '5GbTwMMwJVvrDNXaB9tpaNU9hR38NjbS5MSsUkBvaAYmZFQu': 'ws502.hk5',
    '5HC9dyYcm67xBLB2GGXXeZTbUZTnMbZLkqwTiNDh6W1kAmG2': 'ws502.hk6',
    '5CdGjfoyoX6UQDc9PCs83Lny9bgYMXKjfNfArSznF9PzhR3A': 'ws502.hk7',
    '5FTdrBPbdoDwmLyaYbcmmv2DFMnau5pR3XRGpCXbFJ52CeHQ': 'ws502.hk8',
    '5F9SCMs8f1xdHtCe9sKFVA6P4J7EhDTGydSYXp6nMfqSosdG': 'ws502.hk9',
    '5Fxxy51MJdbphQsAXrWt1uqPzBRAPAhuboFF67812MoBHpwe': 'ws502.hk10',

    '5C83KKjatE4ztzHTu1eAAXc3NszfoQ5kbPgsWLb9R9twddSE': 'ws503.hk1',
    '5Cd1wvj17yWesaX7DrACm3b4X2En53KrPg7ZBE2R5wzrtDP5': 'ws503.hk2',
    '5FNzfvuiSLSXAHRTwRjpKByaeJvj8J5mw76L9JCfxvwjpn2U': 'ws503.hk3',
    '5CX5Dpx12sqYC1EZZeFz39K4WcoJwDE6Npvdy4jk7nWPuzmN': 'ws503.hk4',
    '5EhUpd1Up2YM8BrnefTi2XoNht3H1LWtdcuszKcDuDgrjLQQ': 'ws503.hk5',
    '5CZiBXBJPEqEJpwBw35dDBMWBzM1CpdmWhFSwHnZ83UCVryM': 'ws503.hk6',
    '5CaksEpPfZjWaRQyahTspnq8qvkC33u5fH2FXHwQoPcbfSRj': 'ws503.hk7',
    '5DwCS38kpPCkdxuR8VgnBkFSoA1CaeWLx1schbBWqSKRPy22': 'ws503.hk8',
    '5C5MKHpqS3vJscQDefLN4mpvBfk9yRPuEeJ9XGTmm3khchSB': 'ws503.hk9',
    '5DMP6cGK7HuJnyfexu7oKmzi9W1FwbsSKpfo2WD1JscXKvWj': 'ws503.hk10',

    '5EX2nnZoZ93YgH2CjM2rFvTaJZTHsNGoqVME9quhGkqj5Mr7': 'ws504.hk1',
    '5EoCs4MiAi2AeaUcVhRhP7b6fARoZK1TFEwPHB3PUN9oUceW': 'ws504.hk2',
    '5FH76ztPQH9rbP65Hh6QZ4Yd7DdRJMdopgDC9k4mpaiPAHFG': 'ws504.hk3',
    '5FLX73wnyw1hQrY9JeVPWBY6fj4FEQgVQyuv5oi4Rw6EevgM': 'ws504.hk4',
    '5CcyQFU2sLgj4VDcu3VVfAHZTT5q1f7TnMk4y4PHGZAe4iso': 'ws504.hk5',
    '5CaJz7gYFFWZkmWiMXSuU9AyiWh5aMC2ZpRBvECktKZmMJRL': 'ws504.hk6',
    '5CFKTgsk9NezuHqM5EJrdrKq4LcQUE9hu877wUhfWxjqhE5w': 'ws504.hk7',
    '5HYDBEseofvE5KzmmUBy7XcrYULvYgkMdxG9XizvGGLkJGX8': 'ws504.hk8',
    '5DWzH6HMgXAtUmR1A9HuW2HdMwqes5kK3Hyu8DfDByuVpdJj': 'ws504.hk9',
    '5GR2fn4rLPPs2rZnYbRez49r1aFZJYYW82WHS2G3W1WajkpX': 'ws504.hk10',
}


def get_subnet_reward(netuid, colds, rewards):
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
    df = df[df['COLDKEY'].isin(colds)]
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
        string, has_change = get_subnet_reward(netuid, list(cold_keys.keys()),
                                               rewards)
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
