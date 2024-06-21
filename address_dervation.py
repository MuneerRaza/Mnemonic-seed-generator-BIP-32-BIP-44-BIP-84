import hashlib
from mnemonic import Mnemonic
from bip_utils import Bip44, Bip44Coins, Bip44Changes, Bip49, Bip49Coins, Bip84, Bip84Coins
import multiprocessing as mp

def seed_from_mnemonic(mnemonic):
    mnemo = Mnemonic("english")
    if mnemo.check(mnemonic):
        return mnemo.to_seed(mnemonic)
    else:
        return hashlib.sha256(mnemonic.encode()).digest()

def derive_addresses(seed, paths, num_deposit, num_change):
    addresses = []
    for addr_type, coin_type in paths.items():
        if addr_type == "p2pkh":
            bip44_ctx = Bip44.FromSeed(seed, coin_type)
            for i in range(num_deposit):
                bip44_acc_ctx = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
                address = bip44_acc_ctx.PublicKey().ToAddress()
                addresses.append((addr_type, address))
            for i in range(num_change):
                bip44_acc_ctx = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_INT).AddressIndex(i)
                address = bip44_acc_ctx.PublicKey().ToAddress()
                addresses.append((addr_type + "-change", address))
        elif addr_type == "p2wpkh-p2sh":
            bip49_ctx = Bip49.FromSeed(seed, coin_type)
            for i in range(num_deposit):
                bip49_acc_ctx = bip49_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
                address = bip49_acc_ctx.PublicKey().ToAddress()
                addresses.append((addr_type, address))
            for i in range(num_change):
                bip49_acc_ctx = bip49_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_INT).AddressIndex(i)
                address = bip49_acc_ctx.PublicKey().ToAddress()
                addresses.append((addr_type + "-change", address))
        elif addr_type == "p2wpkh":
            bip84_ctx = Bip84.FromSeed(seed, coin_type)
            for i in range(num_deposit):
                bip84_acc_ctx = bip84_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
                address = bip84_acc_ctx.PublicKey().ToAddress()
                addresses.append((addr_type, address))
            for i in range(num_change):
                bip84_acc_ctx = bip84_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_INT).AddressIndex(i)
                address = bip84_acc_ctx.PublicKey().ToAddress()
                addresses.append((addr_type + "-change", address))
    return addresses

def worker_init(mnemonics, paths, num_deposit, num_change, result_queue):
    global derived_addresses
    derived_addresses = []
    for mnemonic in mnemonics:
        seed = seed_from_mnemonic(mnemonic)
        addresses = derive_addresses(seed, paths, num_deposit, num_change)
        for addr_type, address in addresses:
            derived_addresses.append((mnemonic, addr_type, address))
    result_queue.put(derived_addresses)

def derive_addresses_multiprocessing(mnemonics, paths, num_deposit, num_change):
    result_queue = mp.Queue()
    num_processes = mp.cpu_count()
    chunk_size = len(mnemonics) // num_processes
    processes = []

    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size if i < num_processes - 1 else len(mnemonics)
        process = mp.Process(target=worker_init, args=(mnemonics[start_idx:end_idx], paths, num_deposit, num_change, result_queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    results = []
    while not result_queue.empty():
        results.extend(result_queue.get())

    return results
