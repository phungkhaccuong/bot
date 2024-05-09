import argparse
import time
import os

import logging

def setup_logger():
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Add formatter to console handler
    console_handler.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()

from dotenv import load_dotenv
from pytest import param

import bittensor as bt
import requests

bt.logging.set_debug(False)
load_dotenv()

tele_bot_token = "6408369939:AAHKfnIxyihyXoJ3p1WNN2cgaSD4ielBJtw"
tele_chat_id = "-4151737386"
blocks_since_epoch = 0


def send_tele(text):
    data = {
        "chat_id": tele_chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(
        f'https://api.telegram.org/bot{tele_bot_token}/sendMessage',
        json=data)


def direct_register(subtensor: bt.subtensor, wallet: bt.wallet, hotkey: str):
    subnet = subtensor.get_subnet_info(netuid=netuid)
    success, err_msg = subtensor._do_burned_register(
        netuid=netuid,
        wallet=wallet,
        wait_for_inclusion=False,
        wait_for_finalization=True,
    )

    bt.logging.info(f"[REGISTER] Success: {success}, Error: {err_msg}")
    if success or 'AlreadyRegistered' in err_msg['name']:
        send_tele(
            f'register successfully {netuid} {wallet_name} {hotkey} {subnet.burn}')


def register(subtensor: bt.subtensor, wallet: bt.wallet, hotkey: str, wait_seconds: float=10.6, max_burn=1, target_block=173):
    global blocks_since_epoch
    subnet = subtensor.get_subnet_info(netuid=netuid)
    burn = subnet.burn.__float__()
    new_blocks_since_epoch = subnet.blocks_since_epoch
    #parameters = subtensor.get_subnet_hyperparameters(netuid)

    if blocks_since_epoch != new_blocks_since_epoch:
        bt.logging.info(f"Blocks_since_epoch: {new_blocks_since_epoch}. Burn: {burn}")

    blocks_since_epoch = new_blocks_since_epoch
    if blocks_since_epoch == target_block and burn < max_burn:
        bt.logging.info(f"Block {target_block} reached, waiting for registration: {burn}")
        time.sleep(wait_seconds)
        success, err_msg = subtensor._do_burned_register(
            netuid=netuid,
            wallet=wallet,
            wait_for_inclusion=False,
            wait_for_finalization=True,
        )

        bt.logging.info(f"[REGISTER] Success: {success}, Error: {err_msg}")
        if success or 'AlreadyRegistered' in err_msg['name']:
            send_tele(
                f'register successfully {netuid} {wallet_name} {hotkey} {subnet.burn}')


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
        "--hotkey",
        type=str,
        help="hotkey",
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
    parser.add_argument(
        "--wait_seconds",
        type=float,
        help="seconds to wait until actual burn",
        default=10
    )
    parser.add_argument(
        "--direct",
        action=argparse.BooleanOptionalAction
    )
    parser.add_argument(
        "--target_block",
        type=int,
        help="Block number just before registration",
        default=343
    )
    args = parser.parse_args()

    netuid = args.netuid
    wallet_name = args.wallet_name
    hotkey = args.hotkey
    max_burn = args.max_burn
    network = args.network
    wait_seconds = args.wait_seconds
    target_block =args.target_block

    subtensor = bt.subtensor(network=network)

    wallet = bt.wallet(name=wallet_name, hotkey=hotkey)
    wallet.coldkey

    while True:
        try:
            register(subtensor, wallet, hotkey, wait_seconds=wait_seconds, max_burn=max_burn, target_block=173)
            time.sleep(1)
        except Exception as e:
            bt.logging.error("[REGISTER] Error: ", e)
            time.sleep(30)