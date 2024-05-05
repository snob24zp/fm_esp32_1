
def __is_hex(s):
    return all(c in '0123456789abcdefABCDEF' for c in s)


def __check_str(val, parsed, cfg):
    if str(val).startswith('&'):
        _type = str(val[1:])
        if _type in parsed:
            return parsed[val[1:]]

        if _type in cfg:
            parsed[_type] = __create_item(cfg[_type], parsed, cfg)
            return parsed[_type]

        raise TypeError(f'Unknown type {_type}')

    if str(val).startswith('0x') and __is_hex(str(val[2:])):
        return int(val[2:], 16)
    else:
        return str(val)


def __parse_item(val, parsed, cfg):
    if isinstance(val, dict):
        return __create_item(val, parsed, cfg)
    elif isinstance(val, str):
        return __check_str(val, parsed, cfg)
    elif isinstance(val, (list, tuple)):
        _ret = []
        for _itm in val:
            _ret.append(__parse_item(_itm, parsed, cfg))
        return _ret
    else:
        return val


def __create_item(obj, parsed, cfg):
    _ret = {}

    if isinstance(obj, dict):
        for k in obj:
            if k != 'type' and k != 'import':
                _ret[k] = __parse_item(obj[k], parsed, cfg)
    elif isinstance(obj, (list, tuple)):
        _ret = []
        for _, v in enumerate(obj):
            _ret.append(__parse_item(v, parsed, cfg))
        return _ret

    if 'type' in obj:
        _type = obj['type']
        if 'import' in obj and _type not in globals():
            _path = str(obj['import']).split('.')
            _import = __import__(obj['import'])
            while len(_path) > 1:
                _path = _path[1:]
                _import = _import.__dict__[_path[0]]

            globals()[_type] = _import.__dict__[_type]

        try:
            if _type not in globals():
                globals()[_type] = __import__(_type).__dict__[_type]

            return globals()[_type](**_ret)
        except TypeError as ex:
            # it's a disgusting Pin() kludge
            if 'id' in _ret:
                _id = _ret['id']
                del _ret['id']
                return globals()[_type](_id, **_ret)
            else:
                raise TypeError(f'Could not apply args on {_type} ({ex})')

    return _ret


def gen_bsp(obj):
    _ret = {}
    for k in obj:
        if k not in _ret:
            _ret[k] = __create_item(obj[k], _ret, obj)

    return _ret
