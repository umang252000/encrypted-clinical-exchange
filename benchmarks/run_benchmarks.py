import time, json, os, random

DATA_DIR = "cyborg-proxy/data"

def write_fake_blob(i):
    fake_enc = {
        "nonce": os.urandom(12).hex(),
        "ciphertext": os.urandom(256).hex(),
    }
    with open(os.path.join(DATA_DIR, f"bench_{i}.json"), "w") as f:
        json.dump(fake_enc, f)

def benchmark_write(n=10000):
    print(f"Writing {n} encrypted blobs...")
    t0 = time.time()
    for i in range(n):
        write_fake_blob(i)
    t1 = time.time()
    print("Total time:", t1 - t0)
    print("Per blob:", (t1 - t0) / n)

def benchmark_list():
    t0 = time.time()
    files = os.listdir(DATA_DIR)
    t1 = time.time()
    print("List count:", len(files))
    print("List time:", t1 - t0)

def benchmark_fetch(samples=1000):
    files = random.sample(os.listdir(DATA_DIR), samples)
    t0 = time.time()
    for f in files:
        with open(os.path.join(DATA_DIR, f)) as fp:
            json.load(fp)
    t1 = time.time()
    print("Fetch total:", t1 - t0)
    print("Per fetch:", (t1 - t0) / samples)

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    benchmark_write(10000)
    benchmark_list()
    benchmark_fetch()