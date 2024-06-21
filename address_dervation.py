import numpy as np
from mnemonic import Mnemonic
from bip_utils import Bip44, Bip44Coins, Bip44Changes, Bip49, Bip49Coins, Bip84, Bip84Coins
import hashlib
import time
import multiprocessing as mp

# Address derivation paths
derivation_paths = {
    "p2pkh": Bip44Coins.BITCOIN,
    "p2wpkh-p2sh": Bip49Coins.BITCOIN,
    "p2wpkh": Bip84Coins.BITCOIN,
}

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

def derive_addresses_worker(mnemonics, start_idx, end_idx, paths, num_deposit, num_change):
    derived_addresses = []
    for mnemonic in mnemonics[start_idx:end_idx]:
        seed = seed_from_mnemonic(mnemonic)
        addresses = derive_addresses(seed, paths, num_deposit, num_change)
        for addr_type, address in addresses:
            derived_addresses.append((mnemonic, addr_type, address))
    return derived_addresses

def derive_addresses_gpu(mnemonics, num_deposit, num_change):
    print("Address derivation started...")
    start_time = time.time()
    # Parallel processing setup
    num_processes = mp.cpu_count()
    chunk_size = len(mnemonics) // num_processes
    chunks = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_processes)]
    chunks[-1] = (chunks[-1][0], len(mnemonics))

    # Create a pool of processes
    pool = mp.Pool(processes=num_processes)

    # Map the worker function to each chunk
    results = pool.starmap(derive_addresses_worker, [(mnemonics, start, end, derivation_paths, num_deposit, num_change) for start, end in chunks])

    # Close the pool and wait for all processes to finish
    pool.close()
    pool.join()

    end_time=time.time()
    total_time = end_time - start_time

    derived_addresses = []
    for result in results:
        derived_addresses.extend(result)

    num_addresses_generated = len(derived_addresses)
    addresses_per_second = num_addresses_generated / total_time

    # print(f"Total time taken: {total_time:.4f} seconds")
    # print(f"Number of addresses generated: {num_addresses_generated}")
    # print(f"Addresses generated per second: {addresses_per_second:.4f}")
    # print("Address derivation completed.")

    return derived_addresses

