import argparse
import time
import os

import bittensor as bt
import requests

old_burn = 0
registered_map = {}

tele_bot_token = os.getenv("TELE_REPORT_TOKEN")
tele_chat_id = os.getenv("TELE_CHAT_ID")

def send_tele(text):
    data = {
        "chat_id": tele_chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(
        f'https://api.telegram.org/bot{tele_bot_token}/sendMessage',
        json=data)


def main(subtensor: bt.subtensor, wallet: bt.wallet, hotkey: str):
    global old_burn
    subnet = subtensor.get_subnet_info(netuid=netuid)

    burn = subnet.burn.__float__()
    if old_burn == 0:
        old_burn = burn
    if old_burn == burn:
        return

    bt.logging.info(f"[REGISTER] Burn: {burn}, Old Burn: {old_burn}")
    old_burn = burn

    if burn < max_burn:
        success, err_msg = subtensor._do_burned_register(
            netuid=netuid,
            wallet=wallet,
            wait_for_inclusion=False,
            wait_for_finalization=True,
        )

        bt.logging.info(f"[REGISTER] Success: {success}, Error: {err_msg}")
        if success or 'AlreadyRegistered' in err_msg['name']:
            registered_map[hotkey] = True
            send_tele(
                f'register successfully {netuid} {wallet_name} {hotkey} {burn}')
        # else:
        #     send_tele(
        #         f'register failed {netuid} {wallet_name} {hotkey} {burn} {err_msg}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--netuid",
        type=int,
        help="netuid",
        required=True
    )
    parser.add_argument(
        "--wallet_name",
        type=str,
        help="wallet name",
        required=True
    )
    parser.add_argument(
        "--hotkeys",
        type=str,
        help="hotkeys",
        required=True
    )
    parser.add_argument(
        "--max_burn",
        type=float,
        help="max burn",
        required=True
    )
    parser.add_argument(
        "--network",
        type=str,
        help="network",
        default='local'
    )
    args = parser.parse_args()

    netuid = args.netuid
    wallet_name = args.wallet_name
    hotkeys = args.hotkeys.split(',')
    max_burn = args.max_burn
    network = args.network

    subtensor = bt.subtensor(network=network)

    while True:
        try:
            for hotkey in hotkeys:
                wallet = bt.wallet(name=wallet_name, hotkey=hotkey)
                wallet.coldkey

                while registered_map.get(hotkey) is None or registered_map[hotkey] \
                        == False:
                    main(subtensor, wallet, hotkey)
                    time.sleep(1)
        except Exception as e:
            bt.logging.error("[REGISTER] Error: ", e)
            # send_tele(f'registered failed {e}')

        time.sleep(60)