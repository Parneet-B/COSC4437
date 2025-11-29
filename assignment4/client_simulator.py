from server_simulator import get_file, try_write

cache = {}

def read(name):
    if name in cache:
        print("[CACHE]", name, "→", cache[name])
        return cache[name]

    v = get_file(name)
    cache[name] = v
    print("[READ]", name, "=", v)
    return v

def write(name, new_value):
    print("\n[CLIENT WRITE]", name)

    ok = try_write(name, new_value)
    if not ok:
        print("Write denied (no quorum)")
        return

    if name in cache:
        del cache[name]

    print("Write applied; cache cleared")

if __name__ == "__main__":
    read("file1.txt")
    write("file1.txt", "New content from client")
    read("file1.txt")

    print("\nCache:", cache)
