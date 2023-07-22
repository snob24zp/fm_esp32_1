class bit:
    def __init__(self, value = 0) -> None:
        self.value = value
        
    def __getitem__(self, key: int):
        if isinstance(key, int):
            return bool(self.value & 1 << key)

        raise Exception(f'{key} is not int')

    def __setitem__(self, key: int, value: bool):
        value = bool(value)
        if value:
            self.value |= 1 << key 
        else:
            self.value &=~(1 << key)

    def __delitem__(self, key):
        self[key] = False

    def __contains__(self, key):
        return self.value > (1<<key)
