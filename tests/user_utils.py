import hmac
import hashlib
import base64
import struct


def sign(key: bytes, msg: str):
    '''
    Подписывает сообщение
    :param key: Ключ
    :param msg: Сообщение
    '''
    return base64.b64encode(hmac.new(key=key, msg=msg.encode('utf-8'), digestmod=hashlib.sha256).digest()).decode('utf-8')


def check(key: bytes, value: str):
    '''
    Проверяет входящее значение hmac на соответствие пользователю
    :return: Если hmac соотвествует пользователю, будет возвращен обрезанное значение до комманды устройства, иначе None
    '''
    value = str(value).rsplit('.', 1)
    if len(value) > 1:
        income_sign = base64.b64decode(value[1])
        msg = bytes(value[0], encoding='utf-8')
        calc_sign = hmac.new(key=key, msg=msg, digestmod=hashlib.sha256).digest()
        if calc_sign == income_sign:
            return value[0]
        return None

    return value[0]


def create_key(user: str, pwd: str):
    '''
    Создает ключ пользователя из логина и пароля
    '''
    res = bytearray(user.encode())
    res.append(0)
    res.extend(pwd.encode())
    return hashlib.sha256(res).digest()


def create_user(key: bytes, perm: int, user: str, acl: list) -> bytes:
    res = bytearray(key)
    res.append(perm & 0xff)
    user = user.encode()
    user += bytes(64 - len(user))
    res.extend(user)
    for a in acl:
        res.extend(struct.pack('<h', a))

    return bytes(res)
