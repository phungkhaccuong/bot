if __name__ == '__main__':
    uid = [1,4,6,8,9,4,5,6]
    distinct_subnet_ids = list(set(uid))
    for net_id in distinct_subnet_ids:
        print(net_id)