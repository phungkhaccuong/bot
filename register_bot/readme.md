# Quickstart

## Bước 1:

Chạy file block_burn.py để tự động lấy target block burn. Cú pháp như sau:
```bash
pm2 start register_bot/block_burn.py --interpreter python3 --name "target-block" -- --netuid <netuid>
```
## Bước 2:
Sau khi lấy được target block ( trong file target_block_burn.json) của subnet, chạy bot đăng kí

```bash
pm2 start register_bot/block_register.py --interpreter python3 --name "new_bot" -- --netuid <netuid> --wallet_name <coldkey>  --hotkey <hotkey> --network finney --wait_seconds 11 --max_burn 3
```
