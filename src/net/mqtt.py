import gc
import ssl
from net.umqtt_simple import MQTTClient  # Ваш новый путь к официальному клиенту

def on_msg(topic, msg):
    print("Получено сообщение:", topic.decode(), msg.decode())

def test():
    print("=== ЗАПУСК ОТЛАДКИ AWS MQTT (ФИНАЛЬНЫЙ ВАРИАНТ) ===")
    
    gc.collect()
    print("FREE BEFORE CONNECT =", gc.mem_free())

    # 1. Читаем бинарные файлы сертификатов из папки certs/
    try:
        with open('certs/ecc-crt.der', 'rb') as f: #ecc-crt # cert
            client_cert = f.read()
        with open('certs/ecc-key.der', 'rb') as f: #ecc-key # key
            client_key = f.read()
        with open('certs/rootCA3.der', 'rb') as f: # rootCA3  # root_ca
            root_ca = f.read()    
    except OSError:
        print("Ошибка: Не найдены файлы в папке certs/")
        return

    # 2. Собираем классический словарь ssl_params для mbedtls
    ssl_params = {
        "cert": client_cert,
        "key": client_key,
        "cadata": root_ca,
        "server_side": False
    }

    # Мгновенно чистим дубликаты из RAM перед подключением
    del client_cert
    del client_key
    del root_ca
    gc.collect()

    # 3. Инициализируем официальный клиент, передавая ssl_params напрямую
    server_host = 'a3bb1kruav9c9p-ats.iot.eu-central-1.amazonaws.com'
    
    mq = MQTTClient(
        client_id='esp32-c3-bridge',
        server=server_host,
        port=8883,
        ssl=True,              # Включаем SSL
        ssl_params=ssl_params,  # Передаем словарь параметров напрямую сюда
        keepalive=60
    )
    
    mq.set_callback(on_msg)

    # 4. Подключение
    try:
        print("Выполняется mq.connect()...")
        mq.connect()
        print("УСПЕШНО ПОДКЛЮЧЕНО К AWS IOT CORE!")
        
        topic_sub = b">/17:91:a8:06:f4:fc/4243850"
        mq.subscribe(topic_sub)
        print("Успешная подписка на топик")
        
        for _ in range(10):
            mq.check_msg()
            import time
            time.sleep(1)
            
    except Exception as e:
        print("Ошибка при работе с AWS MQTT:", e)

    # ВРЕМЕННО: Останавливаем систему здесь, чтобы освободить RAM 
    # и не дать запуститься фоновому коннекту к x.ks.ua
    import sys
    print("Тест завершен. Принудительный останов.")
    sys.exit()    