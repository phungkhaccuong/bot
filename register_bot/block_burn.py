import argparse
import json
import time

import bittensor as bt
from dotenv import load_dotenv

bt.logging.set_debug(False)
load_dotenv()
blocks_since_epoch = 0
old_burn = -1
file_name = 'target_block_burn.json'


def load_target_block_burn_of_all_subnet():
    with open(file_name, 'r') as json_file:
        target_block_burn = json.load(json_file)
    return target_block_burn


def save_target_block_burn_of_all_subnet(data):
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file)


def find_target_block_burn(new_blocks_since_epoch):
    target_block_burn = new_blocks_since_epoch - 2
    if target_block_burn == -1:
        target_block_burn = 359
    elif target_block_burn == -2:
        target_block_burn = 358
    return target_block_burn


def update_block_burn_of_subnet(netuid, new_blocks_since_epoch):
    key = f"SN_{netuid}"
    target_block_burns = load_target_block_burn_of_all_subnet()
    bt.logging.info(f"target_block_burns::{target_block_burns}")
    if key in target_block_burns:
        target_block_burn = find_target_block_burn(new_blocks_since_epoch)
        target_block_burns[key] = target_block_burn
        save_target_block_burn_of_all_subnet(target_block_burns)
        bt.logging.info(f"update_block_burn_of_subnet of {key} with value {target_block_burn} successful!!!")
    else:
        raise Exception(f"Cannot find key {key} in target_block_burns file")


def update_target_block_burn(subtensor: bt.subtensor, netuid):
    global blocks_since_epoch, old_burn
    subnet = subtensor.get_subnet_info(netuid=netuid)
    burn = subnet.burn.__float__()
    new_blocks_since_epoch = subnet.blocks_since_epoch

    if old_burn == -1:
        old_burn = burn

    if blocks_since_epoch != new_blocks_since_epoch:
        bt.logging.info(f"Subnet:{netuid}. Blocks_since_epoch: {new_blocks_since_epoch}. Burn: {burn}")
        # if old_burn != burn:
        #     update_block_burn_of_subnet(netuid, new_blocks_since_epoch)
        #     old_burn = burn

        update_block_burn_of_subnet(netuid, new_blocks_since_epoch)
        old_burn = burn

    blocks_since_epoch = new_blocks_since_epoch


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--netuid",
        type=int,
        help="netuid",
        required=True
    )

    args = parser.parse_args()
    netuid = args.netuid
    subtensor = bt.subtensor('finney')

    while True:
        try:
            update_target_block_burn(subtensor, netuid)
            time.sleep(3)
        except Exception as e:
            bt.logging.error("[REGISTER] Error: ", e)
            time.sleep(30)
