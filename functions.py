import requests
from prettytable import PrettyTable
import pandas as pd
from io import StringIO


def send_balance_report(subtensor, cold_keys, total_map, tele_chat_id,
                        tele_report_token):
    table = PrettyTable()
    table.field_names = ["NAME", "FREE", "STAKED", "TOTAL", "DAILY REWARDS"]

    coldkeys = list(cold_keys.keys())
    print(f"coldkey::{coldkeys}")
    wallet_values = list(cold_keys.values())
    print(f"wallet_names::{wallet_values}")

    subnet_ids = [t[1] for t in wallet_values]

    wallet_names = [t[0] for t in wallet_values]

    free_balances = [
        subtensor.get_balance(coldkeys[i]) for i in range(len(coldkeys))
    ]

    print(f"free_balances::{free_balances}")

    staked_balances = [
        subtensor.get_total_stake_for_coldkey(coldkeys[i])
        for i in range(len(coldkeys))
    ]

    print(f"staked_balances::{staked_balances}")

    daily_rewards = get_reward_of_cold_keys(cold_keys)

    print(f"daily_rewards::{daily_rewards}")

    balances = {
        name: (subnet_id, coldkey, free, staked, daily_reward)
        for name, subnet_id, coldkey, free, staked, daily_reward in sorted(
            zip(wallet_names, subnet_ids, coldkeys, free_balances, staked_balances, daily_rewards)
        )
    }

    print(f"balancessssssssssssssssss::{balances}")


    total_free_balance = sum(free_balances)
    total_staked_balance = sum(staked_balances)
    total_daily_reward = sum(daily_rewards)

    has_change = False
    # for name, (coldkey, free, staked, daily_reward) in balances.items():
    #     total = free + staked
    #
    #     arrow = ''
    #     if coldkey in total_map:
    #         if total_map[coldkey] > total:
    #             arrow = '↓'
    #             has_change = True
    #         elif total_map[coldkey] < total:
    #             arrow = '↑'
    #             has_change = True
    #     else:
    #         has_change = True
    #
    #     table.add_row([
    #         name,
    #         '{0:.3f}'.format(free.__float__()),
    #         '{0:.3f}'.format(staked.__float__()),
    #         '{0:.3f}'.format(total.__float__()) + arrow,
    #         '{0:.3f}'.format(daily_reward.__float__()),
    #     ])
    #
    #     total_map[coldkey] = total
    # table.add_row(["-", "-", "-", "-", "-"])
    # table.add_row([
    #     "All",
    #     '{0:.3f}'.format(total_free_balance.__float__()),
    #     '{0:.3f}'.format(total_staked_balance.__float__()),
    #     '{0:.3f}'.format((total_free_balance +
    #                       total_staked_balance).__float__()),
    #     '{0:.3f}'.format(total_daily_reward.__float__()),
    # ])
    #
    # if has_change:
    #     data = {
    #         "chat_id": tele_chat_id,
    #         "text": f'Balance<pre>{table.get_string()}</pre>',
    #         "parse_mode": "HTML"
    #     }
    #
    #     requests.post(
    #         f'https://api.telegram.org/bot{tele_report_token}/sendMessage',
    #         json=data)


def send_balance_report_v1(subtensor, cold_keys, total_map, tele_chat_id,
                        tele_report_token):
    table = PrettyTable()
    table.field_names = ["NAME", "FREE", "STAKED", "TOTAL", "DAILY REWARDS"]

    coldkeys = list(cold_keys.keys())
    wallet_names = list(cold_keys.values())

    free_balances = [
        subtensor.get_balance(coldkeys[i]) for i in range(len(coldkeys))
    ]

    staked_balances = [
        subtensor.get_total_stake_for_coldkey(coldkeys[i])
        for i in range(len(coldkeys))
    ]

    daily_rewards = get_reward_of_cold_keys(cold_keys)

    balances = {
        name: (coldkey, free, staked, daily_reward)
        for name, coldkey, free, staked, daily_reward in sorted(
            zip(wallet_names, coldkeys, free_balances, staked_balances, daily_rewards)
        )
    }

    total_free_balance = sum(free_balances)
    total_staked_balance = sum(staked_balances)
    total_daily_reward = sum(daily_rewards)

    has_change = False
    for name, (coldkey, free, staked, daily_reward) in balances.items():
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
            '{0:.3f}'.format(free.__float__()),
            '{0:.3f}'.format(staked.__float__()),
            '{0:.3f}'.format(total.__float__()) + arrow,
            '{0:.3f}'.format(daily_reward.__float__()),
        ])

        total_map[coldkey] = total
    table.add_row(["-", "-", "-", "-", "-"])
    table.add_row([
        "All",
        '{0:.3f}'.format(total_free_balance.__float__()),
        '{0:.3f}'.format(total_staked_balance.__float__()),
        '{0:.3f}'.format((total_free_balance +
                          total_staked_balance).__float__()),
        '{0:.3f}'.format(total_daily_reward.__float__()),
    ])

    if has_change:
        data = {
            "chat_id": tele_chat_id,
            "text": f'Balance<pre>{table.get_string()}</pre>',
            "parse_mode": "HTML"
        }

        requests.post(
            f'https://api.telegram.org/bot{tele_report_token}/sendMessage',
            json=data)


def get_subnet_data(netuid):
    url = 'https://taostats.io/wp-admin/admin-ajax.php'
    data = {
        'action': 'metagraph_table',
        'this_netuid': netuid
    }

    response = requests.post(url, data=data)

    tables = pd.read_html(StringIO(response.text))
    return tables[0]


def get_reward_of_cold_keys(cold_keys):
    uids = [10, 23, 28, 16, 25]
    df = pd.DataFrame()
    payload = []
    for uid in uids:
        payload.append(get_subnet_data(uid))
    df = pd.concat([df] + payload, ignore_index=True)

    df = df[df['COLDKEY'].isin(cold_keys)]
    daily_rewards = []
    for cold_key in cold_keys:
        reward = 0
        for index, row in df.iterrows():
            if cold_key == row['COLDKEY']:
                reward += row['DAILY REWARDS']

        daily_rewards.append(reward)

    print(daily_rewards)
    return daily_rewards


def get_subnet_reward(netuid, cold_keys, rewards, reward_map, hotkeys):
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


def send_miner_report(my_netuids, cold_keys, tele_chat_id, tele_report_token,
                       reward_map, hotkeys):
    text = ''
    rewards = []
    need_send = False
    for netuid in my_netuids:
        string, has_change = get_subnet_reward(netuid, list(cold_keys.keys()),
                                               rewards, reward_map, hotkeys)
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

    result = requests.post(
        f'https://api.telegram.org/bot{tele_report_token}/sendMessage',
        json=data)
    print(result)

def get_keys_rank_under_50(my_netuids, cold_keys, tele_chat_id, tele_report_token, reward_map, hotkeys):
    text = ''
    rewards = []
    need_send = False
    string, has_change = get_subnet_reward_v1(my_netuids, list(cold_keys.keys()), rewards, reward_map, hotkeys)
    if has_change:
        need_send = True
    if string != '':
        text += f'\n Rank keys under 50 <pre>{string}</pre>'


    if not need_send:
        return

    data = {
        "chat_id": tele_chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    result = requests.post(
        f'https://api.telegram.org/bot{tele_report_token}/sendMessage',
        json=data)
    print(result)

def get_subnet_reward_v1(netuids, cold_keys, rewards, reward_map, hotkeys):
    has_change = True
    netuids = [10, 23, 28, 16, 25]
    x = PrettyTable()
    x.field_names = ["SUBNET", "UID", "HOT", "INCENTIVE", "REWARDS", "RANK"]
    for net_id in netuids:
        url = 'https://taostats.io/wp-admin/admin-ajax.php'
        data = {
            'action': 'metagraph_table',
            'this_netuid': net_id
        }

        response = requests.post(url, data=data)

        tables = pd.read_html(StringIO(response.text))
        df = tables[0].sort_values(by='INCENTIVE', ascending=True)
        incentives = df['INCENTIVE']

        df = df[df['COLDKEY'].isin(cold_keys)]
        if df.empty:
            return '', has_change

        incentives = incentives[incentives > 0]

        for index, row in df.iterrows():
            if incentives[incentives < row['INCENTIVE']].count() + 1 > 50:
                continue

            key = f'{net_id}_{row["UID"]}'
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

            reward_map[key] = row['DAILY REWARDS']
            hot_name = hotkeys.get(row['HOTKEY'], '')
            x.add_row([f"SN_{net_id}", row['UID'], hot_name, row['INCENTIVE'],
                       '{0:.3f}'.format(row['DAILY REWARDS']) + arrow,
                       incentives[incentives < row['INCENTIVE']].count() + 1])

    return x.get_string(), has_change