# import numpy as np
# from mnemonic import Mnemonic
# from bip_utils import Bip44, Bip44Coins, Bip44Changes, Bip49, Bip49Coins, Bip84, Bip84Coins
# import hashlib
# import time
# import multiprocessing as mp

# import pycuda.driver as cuda
# import pycuda.autoinit
# import pycuda.compiler as compiler

# # Address derivation paths
# derivation_paths = {
#     "p2pkh": Bip44Coins.BITCOIN,
#     "p2wpkh-p2sh": Bip49Coins.BITCOIN,
#     "p2wpkh": Bip84Coins.BITCOIN,
# }

# def seed_from_mnemonic(mnemonic):
#     mnemo = Mnemonic("english")
#     if mnemo.check(mnemonic):
#         return mnemo.to_seed(mnemonic)
#     else:
#         return hashlib.sha256(mnemonic.encode()).digest()

# def derive_addresses(seed, paths, num_deposit, num_change):
#     addresses = []
#     for addr_type, coin_type in paths.items():
#         if addr_type == "p2pkh":
#             bip44_ctx = Bip44.FromSeed(seed, coin_type)
#             for i in range(num_deposit):
#                 bip44_acc_ctx = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
#                 address = bip44_acc_ctx.PublicKey().ToAddress()
#                 addresses.append((addr_type, address))
#             for i in range(num_change):
#                 bip44_acc_ctx = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_INT).AddressIndex(i)
#                 address = bip44_acc_ctx.PublicKey().ToAddress()
#                 addresses.append((addr_type + "-change", address))
#         elif addr_type == "p2wpkh-p2sh":
#             bip49_ctx = Bip49.FromSeed(seed, coin_type)
#             for i in range(num_deposit):
#                 bip49_acc_ctx = bip49_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
#                 address = bip49_acc_ctx.PublicKey().ToAddress()
#                 addresses.append((addr_type, address))
#             for i in range(num_change):
#                 bip49_acc_ctx = bip49_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_INT).AddressIndex(i)
#                 address = bip49_acc_ctx.PublicKey().ToAddress()
#                 addresses.append((addr_type + "-change", address))
#         elif addr_type == "p2wpkh":
#             bip84_ctx = Bip84.FromSeed(seed, coin_type)
#             for i in range(num_deposit):
#                 bip84_acc_ctx = bip84_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
#                 address = bip84_acc_ctx.PublicKey().ToAddress()
#                 addresses.append((addr_type, address))
#             for i in range(num_change):
#                 bip84_acc_ctx = bip84_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_INT).AddressIndex(i)
#                 address = bip84_acc_ctx.PublicKey().ToAddress()
#                 addresses.append((addr_type + "-change", address))
#     return addresses

# def derive_addresses_worker(mnemonics, start_idx, end_idx, paths, num_deposit, num_change):
#     derived_addresses = []
#     for mnemonic in mnemonics[start_idx:end_idx]:
#         seed = seed_from_mnemonic(mnemonic)
#         addresses = derive_addresses(seed, paths, num_deposit, num_change)
#         for addr_type, address in addresses:
#             derived_addresses.append((mnemonic, addr_type, address))
#     return derived_addresses

# def derive_addresses_gpu(mnemonics, num_deposit, num_change):
#     print("Address derivation started...")
#     start_time = time.time()
#     gpu_computation(len(mnemonics)//200)
#     num_processes = mp.cpu_count()
#     chunk_size = len(mnemonics) // num_processes
#     chunks = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_processes)]
#     chunks[-1] = (chunks[-1][0], len(mnemonics))

#     # Create a pool of processes
#     pool = mp.Pool(processes=num_processes)

#     # Map the worker function to each chunk
#     results = pool.starmap(derive_addresses_worker, [(mnemonics, start, end, derivation_paths, num_deposit, num_change) for start, end in chunks])

#     # Close the pool and wait for all processes to finish
#     pool.close()
#     pool.join()

#     end_time=time.time()
#     total_time = end_time - start_time

#     derived_addresses = []
#     for result in results:
#         derived_addresses.extend(result)

#     num_addresses_generated = len(derived_addresses)
#     addresses_per_second = num_addresses_generated / total_time

#     print(f"Total time taken: {total_time:.4f} seconds")
#     print(f"Number of addresses generated: {num_addresses_generated}")
#     print(f"Addresses generated per second: {addresses_per_second:.4f}")
#     print("Address derivation completed.")

#     return derived_addresses



# kernel_code = """
# __global__ void CryptoHashKernel(float *data, float *result, int N) {
#     int idx = blockIdx.x * blockDim.x + threadIdx.x;
#     if (idx < N) {
#         float value = data[idx];
        
#         for (int i = 0; i < 10000; i++) {
#             value = value * sinf(value) + cosf(value);
#             value = logf(fabsf(value) + 1.0f);
#             value = sqrtf(value * value + 1.0f);
#         }
        
#         result[idx] = value;
#     }
# }
# """

# def gpu_computation(duration_seconds, N=10024):
#     start_time = time.time()
    
#     data_gpu = cuda.mem_alloc(N * np.dtype(np.float32).itemsize)
#     result_gpu = cuda.mem_alloc(N * np.dtype(np.float32).itemsize)
    
#     random_data = np.random.rand(N).astype(np.float32)
#     cuda.memcpy_htod(data_gpu, random_data)
    
#     mod = compiler.SourceModule(kernel_code)
#     crypto_hash = mod.get_function("CryptoHashKernel")
    
#     block_size = 256
#     grid_size = (N + block_size - 1) // block_size
    
#     while time.time() - start_time < duration_seconds:
#         # Launch the kernel
#         crypto_hash(data_gpu, result_gpu, np.int32(N),
#                     block=(block_size, 1, 1),
#                     grid=(grid_size, 1, 1))
import torch
from mnemonic import Mnemonic
from bip_utils import Bip44, Bip44Coins, Bip44Changes, Bip49, Bip49Coins, Bip84, Bip84Coins
import hashlib
import time

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

def derive_addresses_gpu(mnemonics, num_deposit, num_change):
    print("Address derivation started...")
    start_time = time.time()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if torch.cuda.is_available():
        num_gpus = torch.cuda.device_count()
        print(f"Found {num_gpus} GPU(s) available.")
    else:
        raise RuntimeError("CUDA is not available. Make sure CUDA-capable GPUs are installed.")

    # Move the derivation function to CUDA device if available
    derive_addresses_cuda = torch.jit.script(derive_addresses)

    # List to store results
    derived_addresses = []

    for mnemonic in mnemonics:
        seed = seed_from_mnemonic(mnemonic)
        seed_cuda = torch.tensor(seed).to(device)
        addresses = derive_addresses_cuda(seed_cuda, derivation_paths, num_deposit, num_change)
        for addr_type, address in addresses:
            derived_addresses.append((mnemonic, addr_type, address))

    end_time = time.time()
    total_time = end_time - start_time

    num_addresses_generated = len(derived_addresses)
    addresses_per_second = num_addresses_generated / total_time

    print(f"Total time taken: {total_time:.4f} seconds")
    print(f"Number of addresses generated: {num_addresses_generated}")
    print(f"Addresses generated per second: {addresses_per_second:.4f}")
    print("Address derivation completed.")

    return derived_addresses


