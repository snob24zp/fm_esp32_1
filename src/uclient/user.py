try:
    from micropython import const
except ImportError:
    def const(ret):
        return ret


class user_base:
    
    USER_ACL_REG_READ = const(1)   # уведомление об изменениях регистров
    USER_ACL_REG_WRITE = const(2)  # изменение значения регистров
    USER_ACL_MEM_READ = const(4)   # считывание память
    USER_ACL_MEM_WRITE = const(8)  # Пользователь может записывать память
    USER_ACL_FW = const(0x10)      # Пользователь может обновлять прошивку
    USER_ACL_EVT = const(0x20)     # Пользователь может получать список событий
    USER_ACL_USR = const(0x40)     # Пользователь может изменять список пользователей
    USER_ACL_RST = const(0x80)     # сбрасывать устройство в заводские значения
    
    def __init__(self, name : str, uid: bytes, perm: int) -> None:
        self.name = name
        self.uid = uid
        self.perm = perm

    @staticmethod
    def from_dict(user_dict: dict):
        return user_base(name=user_dict['n'], uid=bytes.fromhex(user_dict['u']), perm=user_dict['p'])

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        
        raise Exception(f'{key} is not found')

    def __setitem__(self, key, value):
        if hasattr(self, key):
            return setattr(self, key, value)

    def __delitem__(self, key):
        delattr(self, key)

    def __contains__(self, key):
        return hasattr(self, key)

    def serialize(self):
        return {"u": self.uid.hex(), "n": self.name, "p": self.perm }

def test():
    assert(user_base('name',b'1234',0).serialize() == {'u': '31323334', 'n': 'name', 'p': 0})