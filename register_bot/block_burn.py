import argparse
import json
import time

import bittensor as bt
from dotenv import load_dotenv

bt.logging.set_debug(False)
load_dotenv()
blocks_since_epoch = 0
old_burn = -1
path_file_name = 'register_bot/target_block_burn.json'


def create_key_in_json_file(netuid):
    return f"SN_{netuid}"


def load_target_block_burn_of_all_subnet():
    with open(path_file_name, 'r') as json_file:
        target_block_burn = json.load(json_file)
    return target_block_burn


def save_target_block_burn_of_all_subnet(data):
    with open(path_file_name, 'w') as json_file:
        json.dump(data, json_file)


def find_target_block_burn(new_blocks_since_epoch):
    target_block_burn = new_blocks_since_epoch - 2
    if target_block_burn == -1:
        target_block_burn = 360
    elif target_block_burn == -2:
        target_block_burn = 359
    return target_block_burn


def update_block_burn_of_subnet(netuid, new_blocks_since_epoch):
    key = create_key_in_json_file(netuid)
    target_block_burns = load_target_block_burn_of_all_subnet()
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

    if is_ignore_block(netuid, new_blocks_since_epoch):
        return

    if blocks_since_epoch != new_blocks_since_epoch:
        bt.logging.info(f"Subnet:{netuid}. Blocks_since_epoch: {new_blocks_since_epoch}. Burn: {burn}")
        if old_burn != burn:
            update_block_burn_of_subnet(netuid, new_blocks_since_epoch)
            old_burn = burn

    blocks_since_epoch = new_blocks_since_epoch


def is_ignore_block(netuid, new_blocks_since_epoch):
    if netuid == 1 and new_blocks_since_epoch == 296:
        return True
    if netuid == 2 and new_blocks_since_epoch == 297:
        return True
    if netuid == 3 and new_blocks_since_epoch == 298:
        return True
    if netuid == 4 and new_blocks_since_epoch == 299:
        return True
    if netuid == 5 and new_blocks_since_epoch == 300:
        return True
    if netuid == 6 and new_blocks_since_epoch == 301:
        return True
    if netuid == 7 and new_blocks_since_epoch == 302:
        return True
    if netuid == 8 and new_blocks_since_epoch == 303:
        return True
    if netuid == 9 and new_blocks_since_epoch == 304:
        return True
    if netuid == 10 and new_blocks_since_epoch == 305:
        return True
    if netuid == 11 and new_blocks_since_epoch == 306:
        return True
    if netuid == 12 and new_blocks_since_epoch == 307:
        return True
    if netuid == 13 and new_blocks_since_epoch == 308:
        return True
    if netuid == 14 and new_blocks_since_epoch == 309:
        return True
    if netuid == 15 and new_blocks_since_epoch == 310:
        return True
    if netuid == 16 and new_blocks_since_epoch == 311:
        return True
    if netuid == 17 and new_blocks_since_epoch == 312:
        return True
    if netuid == 18 and new_blocks_since_epoch == 313:
        return True
    if netuid == 19 and new_blocks_since_epoch == 314:
        return True
    if netuid == 20 and new_blocks_since_epoch == 315:
        return True
    if netuid == 21 and new_blocks_since_epoch == 316:
        return True
    if netuid == 22 and new_blocks_since_epoch == 317:
        return True
    if netuid == 23 and new_blocks_since_epoch == 318:
        return True
    if netuid == 24 and new_blocks_since_epoch == 319:
        return True
    if netuid == 25 and new_blocks_since_epoch == 320:
        return True
    if netuid == 26 and new_blocks_since_epoch == 321:
        return True
    if netuid == 27 and new_blocks_since_epoch == 322:
        return True
    if netuid == 28 and new_blocks_since_epoch == 323:
        return True
    if netuid == 29 and new_blocks_since_epoch == 324:
        return True
    if netuid == 30 and new_blocks_since_epoch == 325:
        return True
    if netuid == 31 and new_blocks_since_epoch == 326:
        return True
    if netuid == 32 and new_blocks_since_epoch == 327:
        return True
    if netuid == 33 and new_blocks_since_epoch == 328:
        return True
    return False


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
            time.sleep(2)
        except Exception as e:
            bt.logging.error("[REGISTER] Error: ", e)
            time.sleep(30)