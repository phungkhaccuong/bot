import requests
from prettytable import PrettyTable
import pandas as pd
from io import StringIO
import json

A_BILLION = 1000000000

MAX_WEIGHTS_LIMIT = 65535


def send_balance_report(subtensor, cold_keys, total_map, tele_chat_id,
                        tele_report_token):
    table = PrettyTable()
    table.field_names = ["NAME", "FREE", "STAKED", "TOTAL", "DAILY REWARDS"]

    coldkeys = list(cold_keys.keys())
    wallet_values = list(cold_keys.values())

    subnet_ids = [t[1] for t in wallet_values]

    free_balances = [
        subtensor.get_balance(coldkeys[i]) for i in range(len(coldkeys))
    ]

    staked_balances = [
        subtensor.get_total_stake_for_coldkey(coldkeys[i])
        for i in range(len(coldkeys))
    ]

    daily_rewards = get_reward_of_cold_keys(cold_keys)

    balances = [
        (subnet_id, free, staked, daily_reward)
        for subnet_id, free, staked, daily_reward in sorted(
            zip(subnet_ids, free_balances, staked_balances, daily_rewards)
        )
    ]

    df = pd.DataFrame(balances, columns=['subnet_id', 'free', 'staked', 'daily_reward'])
    df_agg = df.groupby('subnet_id').agg({'free': 'sum', 'staked': 'sum', 'daily_reward': 'sum'}).reset_index()
    df_agg.insert(df_agg.columns.get_loc('staked') + 1, 'total', df_agg['free'] + df_agg['staked'])
    df_agg = df_agg.sort_values(by='subnet_id')

    total_free_balance = sum(free_balances)
    total_staked_balance = sum(staked_balances)
    total_daily_reward = sum(daily_rewards)

    has_change = False
    for index, row in df_agg.iterrows():
        subnet_id = row['subnet_id']

        arrow = ''
        if subnet_id in total_map:
            if total_map[subnet_id] > row['total']:
                arrow = '↓'
                has_change = True
            elif total_map[subnet_id] < row['total']:
                arrow = '↑'
                has_change = True
        else:
            has_change = True

        table.add_row([
            'ROOT' if subnet_id == 0 else f'SN_{subnet_id}',
            '{0:.3f}'.format(row['free'].__float__()),
            '{0:.3f}'.format(row['staked'].__float__()),
            '{0:.3f}'.format(row['total'].__float__()) + arrow,
            '{0:.3f}'.format(row['daily_reward'].__float__()),
        ])

        total_map[subnet_id] = row['total']
    table.add_row(["-", "-", "-", "-", "-"])
    table.add_row([
        "All",
        '{0:.3f}'.format(total_free_balance.__float__()),
        '{0:.3f}'.format(total_staked_balance.__float__()),
        '{0:.3f}'.format((total_free_balance + total_staked_balance).__float__()),
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


def send_balance_report_old(subtensor, cold_keys, total_map, tele_chat_id,
                            tele_report_token):
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
            '{0:.3f}'.format(free.__float__()),
            '{0:.3f}'.format(staked.__float__()),
            '{0:.3f}'.format(total.__float__()) + arrow
        ])

        total_map[coldkey] = total
    table.add_row(["-", "-", "-", "-"])
    table.add_row([
        "All",
        '{0:.3f}'.format(total_free_balance.__float__()),
        '{0:.3f}'.format(total_staked_balance.__float__()),
        '{0:.3f}'.format((total_free_balance +
                          total_staked_balance).__float__()),
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
    url = "https://api.subquery.network/sq/TaoStats/bittensor-subnets"

    payload = "{\"query\":\"query ($first: Int!, $offset: Int!, $filter: NeuronInfoFilter, $order: [NeuronInfosOrderBy!]!) {\\n\\t\\t\\tneuronInfos(first: $first, offset: $offset, filter: $filter, orderBy: $order) {\\n\\t\\t\\t\\tnodes {\\n\\t\\t\\t\\t\\tid\\n\\t\\t\\t\\t\\tactive\\n\\t\\t\\t\\t\\taxonIp\\n\\t\\t\\t\\t\\taxonPort\\n\\t\\t\\t\\t\\tcoldkey\\n\\t\\t\\t\\t\\tconsensus\\n\\t\\t\\t\\t\\tdailyReward\\n\\t\\t\\t\\t\\tdividends\\n\\t\\t\\t\\t\\temission\\n\\t\\t\\t\\t\\thotkey\\n\\t\\t\\t\\t\\tincentive\\n\\t\\t\\t\\t\\tisImmunityPeriod\\n\\t\\t\\t\\t\\tupdated\\n\\t\\t\\t\\t\\tnetUid\\n\\t\\t\\t\\t\\trank\\n\\t\\t\\t\\t\\tregisteredAt\\n\\t\\t\\t\\t\\tstake\\n\\t\\t\\t\\t\\tuid\\n\\t\\t\\t\\t\\ttrust\\n\\t\\t\\t\\t\\tvalidatorPermit\\n\\t\\t\\t\\t\\tvalidatorTrust\\n\\t\\t\\t\\t}\\n\\t\\t\\t\\tpageInfo {\\n\\t\\t\\t\\t\\tendCursor\\n\\t\\t\\t\\t\\thasNextPage\\n\\t\\t\\t\\t\\thasPreviousPage\\n\\t\\t\\t\\t}\\n\\t\\t\\t\\ttotalCount\\n\\t\\t\\t}\\n\\t\\t}\",\"variables\":{\"offset\":0,\"first\":50,\"filter\":{\"netUid\":{\"equalTo\":10},\"or\":[{\"coldkey\":{\"includesInsensitive\":\"5EAWhStQFp4F5AEG43eokdJtE2ZKwtLuFzcoRdXC2wrru1DZ\"}},{\"coldkey\":{\"includesInsensitive\":\"5ENufmcvZQBhHaCC6UUGAPVzpQk4XvMWsoUzQmLUP1Mpoq9Y\"}},{\"coldkey\":{\"includesInsensitive\":\"5EUc6rY7fup2aH94bCCCuJa41gbRh7C4SvLVPHvVNrcmtB8C\"}}]},\"order\":\"STAKE_DESC\"}}"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    tables = pd.read_html(StringIO(response.text))
    return tables[0]


def get_subnet_data_old(netuid):
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

    return daily_rewards


def get_all_data_subnet(netuid):
    url = "https://api.subquery.network/sq/TaoStats/bittensor-subnets"
    headers = {
        'Content-Type': 'application/json'
    }

    # Initialize a list to store all fetched data
    all_data = []
    total_count = 256  # Total rows you want to fetch
    rows_per_request = 100  # Number of rows per API call
    offset = 0  # Starting offset

    # Loop to fetch data in batches until all rows are fetched
    while offset < total_count:
        payload = {
            "query": """
            query ($first: Int!, $offset: Int!, $filter: NeuronInfoFilter, $order: [NeuronInfosOrderBy!]!) {
                neuronInfos(first: $first, offset: $offset, filter: $filter, orderBy: $order) {
                    nodes {
                        id
                        active
                        axonIp
                        axonPort
                        coldkey
                        consensus
                        dailyReward
                        dividends
                        emission
                        hotkey
                        incentive
                        isImmunityPeriod
                        updated
                        netUid
                        rank
                        registeredAt
                        stake
                        uid
                        trust
                        validatorPermit
                        validatorTrust
                    }
                    pageInfo {
                        endCursor
                        hasNextPage
                        hasPreviousPage
                    }
                    totalCount
                }
            }
            """,
            "variables": {
                "first": rows_per_request,
                "offset": offset,
                "filter": {
                    "netUid": {"equalTo": netuid}
                },
                "order": "STAKE_DESC"
            }
        }

        # Make the POST request to the API
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_data = response.json()
        # Check for errors in the response
        if 'errors' in response_data:
            print("Error in response:", response_data['errors'])
            break

        # Extract the nodes data and add it to the all_data list
        neuron_infos = response_data['data']['neuronInfos']['nodes']
        all_data.extend(neuron_infos)

        # Update the offset for the next iteration
        offset += rows_per_request

    # Verify the number of rows fetched
    print(f"Total rows fetched: {len(all_data)}")

    return all_data


def get_subnet_reward(netuid, cold_keys, rewards, reward_map, hotkeys):
    x = PrettyTable()
    x.field_names = ["INDEX", "UID", "HOT", "INCENTIVE", "REWARDS", "RANK"]

    all_data = get_all_data_subnet(netuid)
    tables = pd.DataFrame(all_data)
    df = tables.sort_values(by='incentive', ascending=True)

    df['dailyReward'] = df['dailyReward'].apply(lambda x: round(x / A_BILLION, 5))
    df['incentive'] = df['incentive'].apply(lambda x: round(x / MAX_WEIGHTS_LIMIT, 5))


    incentives = df['incentive']

    has_change = False
    df = df[df['coldkey'].isin(cold_keys)]
    if df.empty:
        return '', has_change

    incentives = incentives[incentives > 0]

    i = 0
    for index, row in df.iterrows():

        key = f'{netuid}_{row["uid"]}'
        arrow = ''
        if key in reward_map:
            if reward_map[key] > row['dailyReward']:
                arrow = '↓'
                has_change = True
            elif reward_map[key] < row['dailyReward']:
                arrow = '↑'
                has_change = True
        else:
            has_change = True

        i += 1
        reward_map[key] = row['dailyReward']
        hot_name = hotkeys.get(row['hotkey'], '')
        x.add_row([i, row['uid'], hot_name, row['incentive'],
                   '{0:.3f}'.format(row['dailyReward']) + arrow,
                   incentives[incentives < row['incentive']].count() + 1])
        rewards.append(row['dailyReward'])

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
