primary_for = {
    "file1.txt": "NY",
    "file2.txt": "TOR",
    "file3.txt": "LDN"
}

replicas = {
    "NY": {"file1.txt": "Initial file1", "file2.txt": "Initial file2", "file3.txt": "Initial file3"},
    "TOR": {"file1.txt": "Initial file1", "file2.txt": "Initial file2", "file3.txt": "Initial file3"},
    "LDN": {"file1.txt": "Initial file1", "file2.txt": "Initial file2", "file3.txt": "Initial file3"}
}

def get_file(name):
    p = primary_for[name]
    return replicas[p][name]

def try_write(name, content):
    count = len(replicas)
    if count < 2:
        return False

    p = primary_for[name]
    replicas[p][name] = content

    for r in replicas:
        replicas[r][name] = content
    return True
