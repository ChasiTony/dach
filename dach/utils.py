class dotdict(dict):
    def __getattr__(self, key):
        if key not in self:
            raise KeyError()
        val = self[key]
        if isinstance(val, dict):
            return dotdict(val)
        return val
