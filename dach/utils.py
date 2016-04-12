def lookup_dict(d, path):
    keys = list(reversed(path.split('.')))
    val = d[keys.pop()]
    while len(keys) > 0:
        val = val[keys.pop()]
    return val
