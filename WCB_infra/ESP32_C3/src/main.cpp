#include <Arduino.h>/**/





//  ESP32-C3-MINI-1
//  A7672E 

/*
AT+CSQ      уровень сигнала
AT+COPS=?   Список доступных сетей
AT+CRESET   Перезагрузка модуля
AT+CREG?    Проверка регистрации в сети
Первый параметр ответа:  0 – нет кода регистрации сети - плохой знак, позвонить или выйти в интернет не получится
                         1 – есть код регистрации сети
                         2 – есть код регистрации сети + доп. параметры
Второй параметр ответа:  1 – зарегистрирован, домашняя сеть

AT+CPIN?    Проверка наличия SIM-карты   ERROR – возможна ошибка SIM-карты или модема.1ФЕ

AT+GMR          версию прошивки
AT+CFUN=1,1     для перезагрузки
AT+SIMEI?       +SIMEI: 868719072868462

---------------A7600-------
AT+CICCID Считать ICCID с SIM-карты
AT+CIMI Запросить международный идентификатор мобильного абонента

//-------
ATD+380969743152;     звонок
ATH     сбрасывает (отменяет) текущий звонок.


/-----  команды ----
reset    перезагрузка 
sms      отправка SMS
get      Отправка HTTP GET-запроса
tcp      отправка TCP 

 
AT+CPSI?  Проверяем тип сети +CPSI: LTE,Online


AT+SIMCOMATI


  //передача данных через последовательный порт TCP/UDP
  AT+NETOPEN
  AT+CIPRXGET=1
  AT+CIPOPEN=0,"TCP","176.67.8.118",31300
  AT+CIPSEND=0,9
  waveshare
  AT+CIPCLOSE=0
  AT+NETCLOSE


Голосовой вызов:
AT+BINDSIM? Проверьте привязку канала команд AT
+BINDSIM: 0
OK
Привязать к SIM1
AT+DUALSIMURC=2 Включить URC для SIM1 и SIM2
OK
AT+BINDSIM=1 Привязать к SIM2
OK
ATD18412345678; Выполнить голосовой вызов с SIM2, отчет URC для
ATD0969743152;
ATD+380969743152;
SIM2
+CGEVDS: NW ACT 8,


AT+CIMI
AT+SWITCHSIM=? //
AT+SWITCHSIM? //определение главной sim-карты
///AT+SWITCHSIM=0///

at+cereg?
AT+CEREG?

//------------ GPS --- GNSS -------------------------
ATI: Показать идентификационную информацию модуля (производитель, модель, версия прошивки).
Manufacturer: INCORPORATED
Model: A7672E-FASE
Revision: A7672M7_V1.11.1
IMEI: 868719072868462
+GCAP: +CGSM,+FCLASS,+DS

AT

AT+CGNSSPWR=1                   // Включить GNSS
AT+CGNSSPORTSWITCH=1,1
AT+CGPSINFO   или AT+CGNSSTST=1

AT+CGPSINFO:
+CGPSINFO:3113.343286,N,12121.234064,E,250311,072809.3,44.1,0.0,0
OK
AT+CGNSSPWR=?

T+CGNSSSPWR=1 следует выполнить, чтобы включить модуль GNSS в первую очередь.
Информация о местоположении будет выведена на порт USB AT после выполнения AT+CGNSSINFO=<время>, диапазон времени составляет 0-255, единица измерения — секунда, 0 означает отсутствие вывода.
Если информация не зафиксирована или нет сигнала, будут выведены нулевые данные.
Данные, полученные с помощью AT+CGPSINFO и AT+CGNSSINFO, анализируются, выполнение 
AT+CGNSSPORTSWITCH может вывести данные на порт USB AT или порт UART.
Если нужно получить необработанные данные NMEA через порт USB NMEA или порт UART, 
можно реализовать AT+CGNSSPORTSWITCH = 0,0
или AT+CGNSSPORTSWITCH = 0,1.




//------------ GPS ERROR ----------------------------
AT+CGNSPWR=1          // Включить GNSS AT+CGNSSPWR=0
AT+CGNSSEQ="RMC"      // Настроить тип вывода
AT+CGNSINF            // Получить координаты
AT+CGNSRD=1           // Прочитать NMEA строку  AT+CGNSSRD=1 
AT+CGNSPWR=0          // Выключить GNSS

A7672E S2-109ZS - ASR1603E=128M, GNSS(UC6226NIS), BT(ASR5801)

AT+CGNSSMODE

AT+CVAUXV





*/

#include <HardwareSerial.h>
#define TX2    1   //0    // GPIO0 
#define RX2    0   //1    // GPIO1
//#define TX2    0    // GPIO0 
//#define RX2    1    // GPIO1
#define RESET  2    // GPIO1 
#define PWRKEY 3    // GPIO1 
HardwareSerial sim800(1);  // Используем UART1
void resetModule() {
    digitalWrite(RESET, LOW);    
    delay(200);                  //  200 мс
    digitalWrite(RESET, HIGH);  
}
void powerOn() {
    digitalWrite(PWRKEY, LOW);  
    resetModule();
    delay(2000);               //  2000 мс  
    digitalWrite(PWRKEY, HIGH);  
}


 void sendATCommand(String command) {
  Serial1.println(command);   
  delay(1000);
  while (Serial1.available()) {   //  -> A7672E
        String response = Serial1.readString();
        Serial.print("A7672E: ");
        Serial.println(response);  
  }
}

void sendSMS(String phoneNumber, String message) {
  Serial.println("Отправка SMS...");

  Serial1.print("AT+CMGS=\""); 
  Serial1.print(phoneNumber);
  Serial1.println("\"");
  delay(500);

  Serial1.print(message);
  delay(500);

  Serial1.write(26); // Отправка CTRL+Z (код 26)
  Serial.println("SMS отправлено!");
}

void sendGetRequest(String url) {
  Serial.println("Отправка HTTP GET-запроса...");

  sendATCommand("AT+HTTPINIT");  // Инициализация HTTP-сервиса
  sendATCommand("AT+HTTPPARA=\"CID\",1");  
  sendATCommand("AT+HTTPPARA=\"URL\",\"" + url + "\"");  

  sendATCommand("AT+HTTPACTION=0");  // Отправляем GET-запрос
  delay(5000);  // Ждем ответа сервера

  sendATCommand("AT+HTTPREAD");  // Читаем ответ сервера
  sendATCommand("AT+HTTPTERM");  // Завершаем HTTP-сессию
}

void sendTCP(String server, String port, String message) {
  Serial.println("Открываем TCP-соединение...");
 /* sendATCommand("AT+CIPSTART=\"TCP\",\"" + server + "\"," + port);

  Serial.println("Отправка данных...");
  sendATCommand("AT+CIPSEND=" + String(message.length()));
  delay(100);
  sim800.print(message);  // Отправка данных
  sim800.write(26);       // Ctrl+Z для завершения ввода
  delay(3000);
  
  sendATCommand("AT+CIPCLOSE");
  

  //передача данных через последовательный порт TCP/UDP
  AT+NETOPEN
  AT+CIPRXGET=1
  AT+CIPOPEN=0,"TCP","176.67.8.118",31300
  AT+CIPSEND=0,9
  waveshare
  AT+CIPCLOSE=0
  AT+NETCLOSE
  */
}

void setup() {
    pinMode(PWRKEY, OUTPUT);
    pinMode(RESET, OUTPUT);
    
    digitalWrite(PWRKEY, HIGH);  
   
    digitalWrite(RESET, HIGH);   

    Serial.begin(115200);                
    Serial1.begin(115200, SERIAL_8N1, RX2, TX2);  
   
    //Serial1.begin(9600, SERIAL_8N1, RX2, TX2);  
   
    Serial.println("Start esp32-c3!");
    powerOn(); 
    delay(1000); 
    Serial.println("Enable A7672E!");
 // digitalWrite(RESET, LOW);  
  // digitalWrite(PWRKEY, LOW);  
}

void loop() { 

  //  delay(500); Serial1.println("AT+SAPBR=3,1,\"Contype\",\"GPRS\"");   
//Serial1.print("A7672: ");
delay(10);

   if (Serial1.available()) {   //  -> A7672E
        String response = Serial1.readString();
///       Serial.print("ESP32 -> A7672: ");
        Serial.print("A7672: ");
        Serial.println(response);
    }

    if (Serial.available()) {  //COM port
        String cmd = Serial.readString();
        String cmd1 = cmd;
        cmd1.trim(); // Видаляє всі \r і \n
        if(cmd1 == "reset"){          
          ESP.restart(); 
        }else
        if(cmd1 == "sms"){     
          sendATCommand("AT");           // Проверка связи
          sendATCommand("AT+CMGF=1");    // Включаем текстовый режим SMS
          sendATCommand("AT+CSCS=\"GSM\"");  // Устанавливаем кодировку
          sendSMS("+380969743152", "Test ESP32 - SIMCom A7672E!");
        }else
        if(cmd1 == "get"){     
          sendATCommand("AT");                // Проверка связи
          sendATCommand("AT+CPIN?");          // Проверка SIM-карты
          sendATCommand("AT+CREG?");          // Проверка регистрации в сети
          sendATCommand("AT+CSQ");            // Проверка уровня сигнала
          sendATCommand("AT+SAPBR=3,1,\"Contype\",\"GPRS\"");  // Указываем, что соединение через GPRS
          sendATCommand("AT+SAPBR=3,1,\"APN\",\"internet\"");  // Указываем APN (замените на ваш!)
          sendATCommand("AT+SAPBR=1,1");      // Включаем GPRS
          sendATCommand("AT+SAPBR=2,1");      // Получаем IP

          sendGetRequest("http://example.com/data");  // Отправка GET-запроса
        }else
        if(cmd1 == "tcp"){     
          sendATCommand("AT");                // Проверка связи
          sendATCommand("AT+CPIN?");          // Проверка SIM-карты
          sendATCommand("AT+CREG?");          // Проверка регистрации в сети
          sendATCommand("AT+CSQ");            // Проверка уровня сигнала
          // sendATCommand("AT+SAPBR=3,1,\"Contype\",\"GPRS\"");  // Указываем, что соединение через GPRS
          // sendATCommand("AT+SAPBR=3,1,\"APN\",\"internet\"");  // Указываем APN (замените на ваш!)
          // sendATCommand("AT+SAPBR=1,1");      // Включаем GPRS
          // sendATCommand("AT+SAPBR=2,1");      // Получаем IP
          sendATCommand("AT+CNACT=0,1");  // Включаем LTE
          sendATCommand("AT+CNACT?");
          sendTCP("176.67.8.118", "31200", "Test ESP32 - SIMCom A7672E!");
        }else
        if(cmd1 == "tcp_lte"){   

            sendATCommand("AT+CGDCONT=1,\"IP\",\"www.kyivstar.net\"");
        }else
        {         
          Serial1.println(cmd);
        }
        
    }

}
