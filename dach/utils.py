from collections import deque


def lookup_dict(d, path, strict=True):
    keys = deque(path.split('.'))
    while True:
        try:
            d = d[keys.popleft()]
        except KeyError as ke:
            if strict:
                raise ke
            return None
        except IndexError:
            return d
