# Provisioning X.509 certificates for devices

Цей документ описує рекомендований процес отримання X.509 сертифікатів для пристроїв, які підключаються до AWS IoT (або іншого MQTT-брокера), та містить конкретні команди OpenSSL і AWS CLI для двох варіантів: згенерувати ключ/CSR на самому пристрої (рекомендовано) або згенерувати ключі в AWS і завантажити їх на пристрій (менш безпечно).

Важливо: зберігай приватні ключі в безпечному місці. Не зберігай приватні ключі у VCS.

---

## Можливі підходи (вибрати один)

1. Генерувати приватний ключ і CSR на самому пристрої (RECOMMENDED)
   - Приватний ключ ніколи не покидає пристрій — найкраща практика для безпеки.
2. Генерувати ключі і сертифікат в AWS (`create-keys-and-certificate`) і скопіювати їх на пристрій
   - Зручніше для масової підготовки, але приватний ключ створюється поза пристроєм — ризик.

---

## Загальні передумови

- AWS CLI встановлено і налаштовано з обліковими даними, які мають права для AWS IoT (або попросіть адміністратора виконати дії).
- OpenSSL встановлено на машині / пристрої для генерації ключів та CSR (або пристрій має еквівалентні криптографічні інструменти).
- Маєш ім'я IoT policy в AWS (в нашому проекті — `roboscine_device_policy-<accountId>`). Policy повинна дозволяти `iot:AttachPrincipalPolicy`, `iot:CreatePolicy` або давати права publish/subscribe на потрібні топіки.

---

## ВАРІАНТ A — Генерувати ключ і CSR на пристрої (рекомендовано)

1) На самому пристрої (або у secure environment на момент provisioning) генеруємо приватний ключ та CSR:

```bash
# Перейти у робочий каталог
cd /path/to/provisioning

# Згенерувати приватний ключ RSA 2048
openssl genpkey -algorithm RSA -out private.pem.key -pkeyopt rsa_keygen_bits:2048

# Згенерувати CSR; в Common Name (CN) вкажіть унікальний ідентифікатор (наприклад MAC/serial)
openssl req -new -key private.pem.key -out device.csr -subj "/CN=48:3f:da:55:07:5b/3996365522"
```

2) Створити сертифікат у AWS з CSR (сертифікат одразу поставить в `ACTIVE`):

```bash
# Виконати створення сертифіката з CSR
aws iot create-certificate-from-csr \
  --certificate-signing-request file://device.csr \
  --set-as-active \
  --region eu-central-1
```

Команда поверне JSON з полями `certificateArn`, `certificateId` і `certificatePem`. Збережи `certificatePem` у файл (наприкл
ад `device-certificate.pem.crt`) у безпечному каталозі на пристрої.

3) Прикріпити IoT policy до сертифіката (щоб пристрій мав потрібні права):

```bash
# Припускаємо, що policy вже існує (roboscine_device_policy-<accountId>)
aws iot attach-policy \
  --policy-name roboscine_device_policy-832413913020 \
  --target <certificateArn> \
  --region eu-central-1
```

4) (Опціонально) Прив'язати сертифікат до Thing (якщо у вас створені Thing-об'єкти):

```bash
aws iot attach-thing-principal --thing-name <THING_NAME> --principal <certificateArn> --region eu-central-1
```

5) Завантажити Amazon Root CA на пристрій і зберегти файли з правами 600:

```bash
# Amazon Root CA1
curl -o AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem

# Стеж за правами файлів
chmod 600 private.pem.key
chmod 644 AmazonRootCA1.pem
chmod 644 device-certificate.pem.crt
```

6) Тест з’єднання (приклад з mosquitto_pub/sub):

```bash
# endpoint отримати командою:
# aws iot describe-endpoint --endpoint-type iot:Data-ATS --region eu-central-1 --output text --query endpointAddress

mosquitto_sub -h <AWS_IOT_ENDPOINT> -p 8883 --cafile AmazonRootCA1.pem --cert device-certificate.pem.crt --key private.pem.key -t 'test/topic' -d

mosquitto_pub -h <AWS_IOT_ENDPOINT> -p 8883 --cafile AmazonRootCA1.pem --cert device-certificate.pem.crt --key private.pem.key -t 'test/topic' -m 'hello'
```

> Примітка: заміни `<AWS_IOT_ENDPOINT>` на значення з `aws iot describe-endpoint`.

---

## ВАРІАНТ B — Створити ключі і сертифікат у AWS (менш безпечно)

1) Створити ключі та сертифікат у AWS (поверне приватний ключ у відповіді):

```bash
aws iot create-keys-and-certificate --set-as-active --region eu-central-1 --output json
```

2) У відповіді буде `certificatePem`, `keyPair.privateKey` та `certificateArn`. Збережи їх у файли на безпечному комп'ютері і безпечно передай на пристрій.

3) Прикріпити policy до сертифіката:

```bash
aws iot attach-policy --policy-name roboscine_device_policy-832413913020 --target <certificateArn> --region eu-central-1
```

4) Перенести файли (`private.pem.key`, `device-certificate.pem.crt`) на пристрій через захищений канал (scp/rsync-over-ssh), після чого задати права `chmod 600 private.pem.key`.

> Попередження: цей варіант менш безпечний, оскільки приватний ключ створюється поза пристроєм.

---

## Додаткові корисні команди

- Отримати IoT endpoint:
```bash
aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text --region eu-central-1
```

- Створити IoT policy (якщо потрібно):
```bash
aws iot create-policy --policy-name roboscine_device_policy-832413913020 --policy-document file://iot-device-policy.json --region eu-central-1
```

- Перевірити існуючий сертифікат:
```bash
aws iot describe-certificate --certificate-id <certificateId> --region eu-central-1
```

- Відв'язати/видалити сертифікат (коли потрібно відключити пристрій):
```bash
aws iot detach-policy --policy-name roboscine_device_policy-832413913020 --target <certificateArn> --region eu-central-1
aws iot update-certificate --certificate-id <certificateId> --new-status INACTIVE --region eu-central-1
aws iot delete-certificate --certificate-id <certificateId> --region eu-central-1
```

---

## Рекомендації з безпеки

- Генерувати приватний ключ на самому пристрої (Hardware Secure Element або TPM якщо доступні).
- Не зберігати приватні ключі у репозиторії.
- Передавати сертифікати/ключі на пристрій лише через захищені канали (SSH, SFTP, physical provisioning).
- Планувати механізм ротації і відкликання сертифікатів (AWS IoT дозволяє робити `update-certificate` та ставити статус `INACTIVE`).

---

## Приклади і шаблони файлів

- `iot-device-policy.json` — приклад політики для пристрою (приклад):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["iot:Connect"],
      "Resource": ["arn:aws:iot:eu-central-1:832413913020:client/*"]
    },
    {
      "Effect": "Allow",
      "Action": ["iot:Publish","iot:Subscribe","iot:Receive"],
      "Resource": ["arn:aws:iot:eu-central-1:832413913020:topic/*","arn:aws:iot:eu-central-1:832413913020:topicfilter/*"]
    }
  ]
}
```

---

## Примітки

- Налаштування конкретного MQTT-клієнта (в твоєму бекенді) може вимагати додаткових опцій: розташування CA-файлу, формат PEM, клієнтський ID тощо.
- Якщо потрібна автоматизація provisioning (mass provisioning), можна розглянути використання AWS IoT Fleet Provisioning або IoT Device Management workflows.

---

Якщо хочеш — можу додати до `docs/` скрипти для автоматизації (наприклад `scripts/create-csr.sh`, `scripts/aws-provision-from-csr.sh`) та невеликий README з прикладами запуску під Windows/Linux.
