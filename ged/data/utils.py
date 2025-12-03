import hashlib

def hash_file(file):
    hash_func = hashlib.sha256()
    try:
        for chunk in file.chunks():
            hash_func.update(chunk)
    except AttributeError:
        hash_func.update(file)
    return hash_func.hexdigest()
