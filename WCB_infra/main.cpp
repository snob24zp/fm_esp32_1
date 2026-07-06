#include <Arduino.h>

/*

//--------------------------------
WSS
wss://b-edc8a05b-18f7-4fda-ae7a-295969e33aa1-1.mq.eu-central-1.amazonaws.com:61619
username: roboscinemq

password: EeD9YPBkbA448nr



MQTT
mqtt+ssl://b-edc8a05b-18f7-4fda-ae7a-295969e33aa1-1.mq.eu-central-1.amazonaws.com:8883



<GET VERSION>
<SN>
<RESET>
<GET FIRST FILE>
<GET NEXT FILE>

<GET TIME>
<GET DATE>



//----------------------------------
<GET FIRST FILE>
<GET NEXT FILE>
<FCHDIR:settings>     //перейти в каталог
<FREAD:Settings.txt>      //Прочитать


<FCHDIR:results> 
<FCHDIR:Test_results_20250207_19_56> //перейти в каталог
<FCHDIR:Test> //перейти в каталог
  


<FOPEN:test.txt>      //открить файл
<FREAD:test.txt>      //Прочитать
<FCLOSE>              //закрить

<FREAD:log.txt>
-------------------- >17:91:a8:06:f4:fc/4243850920/3  ---------------- Topic
{"id":"082d0111-ccaf-43ea-9a97-087b6eca31c0","command":"<SN>"}
{"id":"082d0111-ccaf-43ea-9a97-087b6eca31c0","command":"<GET FIRST FILE>"}    
{"id":"082d0111-ccaf-43ea-9a97-087b6eca31c0","command":"<GET NEXT FILE>"}
{"id":"082d0111-ccaf-43ea-9a97-087b6eca31c0","command":"<GET FIRST FATR>"}    
{"id":"082d0111-ccaf-43ea-9a97-087b6eca31c0","command":"<GET NEXT FATR>"}
{"id":"082d0111-ccaf-43ea-9a97-087b6eca31c0","command":"<FREAD:log.txt>"}
{"id":"082d0111-ccaf-43ea-9a97-087b6eca31c0","command":"<FREAD:test.txt>"}
{"id":"082d","command":"<FREAD:Settings.txt>"}
сайт  http://roboscine.eu-central-1.elasticbeanstalk.com  
Логин/пароль user@mail.com/1234

<FCHDIR:\>


<GET FIRST FILE>


<FCHDIR:\results>
<FCHDIR:\results\Test_results_20250204_21_21>




{
  "mac": "1b:e6:21:3a:4c:a4",
  "version": "R240503;master;c2667ff72f2b1f6acb109be9b5c2675332675736",
  "type": "mpy",
  "prot": 2,
  "devices": [
    {
      "s": 2756459041,
      "t": 1,
      "r": {
        "0": 2756459041,
        "1": 1751821849
      }
    }
  ]
}

*/

//https://a3bb1kruav9c9p-ats.iot.eu-central-1.amazonaws.com



#include <WiFi.h>
#include <PubSubClient.h>

#include <HardwareSerial.h>
#include <WiFiClientSecure.h>
#include "soc/soc.h"// Отключаем brownout detector
#include "soc/rtc_cntl_reg.h"// Отключаем brownout detector
#include <ArduinoJson.h>

#define UART1_TX 21
#define UART1_RX 20

const char* root_ca_cert = R"EOF(
-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs
N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv
o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU
5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy
rqXRfboQnoZsG4q5WTP468SQvvG5
-----END CERTIFICATE-----
)EOF";

const char* device_cert = R"KEY(
-----BEGIN CERTIFICATE-----
MIIDWTCCAkGgAwIBAgIUd4ztVA0b3/VGUT5Q3LruOHd4TIswDQYJKoZIhvcNAQEL
BQAwTTFLMEkGA1UECwxCQW1hem9uIFdlYiBTZXJ2aWNlcyBPPUFtYXpvbi5jb20g
SW5jLiBMPVNlYXR0bGUgU1Q9V2FzaGluZ3RvbiBDPVVTMB4XDTI1MTExOTEwMDcw
OVoXDTQ5MTIzMTIzNTk1OVowHjEcMBoGA1UEAwwTQVdTIElvVCBDZXJ0aWZpY2F0
ZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMD0um/HfKjhvQ9Hts/3
tzqyEZz4h9gVQJSxgxSfYbvrF0zgkUTNDsP1rxjVGma/4to6ihiLYqgjdQ5Xm9WU
rSvXCeeZQb3CBdkPiBJC3q0dkOQX0/cTaYeEWvdtOfubDps/f9HpwiAMqU7ArdXZ
uOwUUXbOv5+PZ3Rtgta58/5lznNx6GTzi0AlUmtgXx6kNxL4BkGcOfjni4+jacQZ
Colyu57dJK3CjUQD+we6HQcTBi3aLQjA2TGlnLKgUUgrdmXD8oy7IJbXmJ2e1wr/
uqDk0lQW9YnkN2YW9NddB5pxDZXHTKqBCDuh01DXif+UMaZenJQQIQ259RnleKA7
ArECAwEAAaNgMF4wHwYDVR0jBBgwFoAUaBf320QUae2CZ3cnT4B2gR90hy8wHQYD
VR0OBBYEFOI/086MjzfxlcbExcbf1KFiYdCAMAwGA1UdEwEB/wQCMAAwDgYDVR0P
AQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4IBAQBHbNdWeLxZLQTVJ7CAMJChNEzO
cc2ud4ZQed7LfwQ027s118S6MVYhdTJw9k0k7M2MYs/qyZc6f7Y8t4XrE/gDs/dN
JHfoF97NIWFXvOS4+tauOmwpc1dHi1X6wpGYvwjccEjDg24HwTyi0FQBxigJAaKs
/6tIt5Ca0yCOET6+W4fUgeZIP1oYt8BEWyE+6wZk/joDZZx9+BM6gh2+YUeHO7Sf
qaWxcaeJyQXKf4VXiVX87Gs2f9yKTS1hl0wsIFb/tiE1BkUHpq7Xq1Z0yRX2GzSh
wsmWxpMB7bHH9JgjOCa7dLMdw12umjjUO+AIF1NfYAdWnWhi2iUzaP4omPEm
-----END CERTIFICATE-----
)KEY";

const char* private_key = R"KEY(
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAwPS6b8d8qOG9D0e2z/e3OrIRnPiH2BVAlLGDFJ9hu+sXTOCR
RM0Ow/WvGNUaZr/i2jqKGItiqCN1Dleb1ZStK9cJ55lBvcIF2Q+IEkLerR2Q5BfT
9xNph4Ra9205+5sOmz9/0enCIAypTsCt1dm47BRRds6/n49ndG2C1rnz/mXOc3Ho
ZPOLQCVSa2BfHqQ3EvgGQZw5+OeLj6NpxBkKiXK7nt0krcKNRAP7B7odBxMGLdot
CMDZMaWcsqBRSCt2ZcPyjLsglteYnZ7XCv+6oOTSVBb1ieQ3Zhb0110HmnENlcdM
qoEIO6HTUNeJ/5Qxpl6clBAhDbn1GeV4oDsCsQIDAQABAoIBADem3hbbPHMhGHxN
vMZitfAx566UZ+nEx2mbgSjzhybB+Whs5LkpQ3b1Z1kMLZ8w/ObgN3A4022XPG20
iveg+AlK7kpkA3gNe85NEnvh2YOooV+IF9SNPsSdQfdXA4A0CpRwThdnClxgCnzy
SbECKLm+aniPzOjiXX5RD4mK/HqEtU4SswRbi5NA6L35uKxxZXjv8WwWPsVfFUno
XIRlXEYRGlLZJuEN3tNhHOrvZnOINjHGIAPVBOgWNjHDVek1/937Npj5tomB2HyC
qDyyFDF50YB164HqI/Q6UKOIBfD7tIjuL5tAPp4T7jE2wcj9eBDLLEX/rvwXSFXK
XLQCbaECgYEA+vAKjlz54d+LXILKtoGl0CnIlGr5RfrljGeF7ypxvX63vMMcYRUo
V1E4gu6odET33lb1sHWjjr094sKuQIQPVtN+xk1OwLZCdFqdP3AIcfvhOWAWXADN
mZV7w6eri5i4JecLQplWjV7QQHYlhnXMl96vBdxb5tiFFzWdhixW9c0CgYEAxNk+
HEIfo30XKDlu6lMEmyhHcGAUtQwKd00zvR2miI9bdEElo9jln2+IGXtq+T+Xb1KK
bMiR/8K50s22v8udO5tUaj9dbdZyY5Yl5+Z0D9lYnE7jKBHo8w2Mav4BskaOKwod
1+++FEeIyXkyNBTotsJ36QvkKH72BNsCAGXDXHUCgYEApysALUTdJs7wHSn4d0q5
NoqPV+hHtYnmH/nbLK/e47kmF/b20enxXPH7rqXkzMghRBo0RGCqG+4P6x98S/ht
646rdtmLbDA+5xpyhQ9SYPTGXp2XZ6UVUopVz8rEKhQMIRvg0XYrRbRzEW5jo0aY
jFfJyyK4inmVeBe8n+Sr7cUCgYBfG1cW8Bu5McbueFFOha3ECUH62XEnyBmGapaE
2L6NXDYjhRZag4Dt90Uaira0ljTkZEzdIkrn930wjJOvNwFQu0udyd+qIeJCm1jV
IlMRFUHqw3Kc+YpDZFhjmTXYnJ4zzT9+BSchRS6hqRzIbRHCu1KUFlq19iGHVwkw
h/pLwQKBgQDJ/dKi66puGEW+5HxBXVUNzQdYeYVqZJvVizDnC69DOnpqJNdldN/E
TFxlFNDnW9MU/Pl213/EB/u8w6JnZgrHywdTM4pj77DLXs0ybOykXB+Evio6HzvA
J10IpfLqAKCl2frdAe6AGUDgZpFZ+eAvQtepTp3Zs1Vduum9PediMA==
-----END RSA PRIVATE KEY-----
)KEY";

const char* ssid = "TP-Link";
const char* password = "10000001";

const char* mqtt_server = "a3bb1kruav9c9p-ats.iot.eu-central-1.amazonaws.com";
const char* mqtt_client_id = "esp32-c3-bridge";

String id_coom; 
WiFiClientSecure espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
//#define MSG_BUFFER_SIZE	(2048)
#define MSG_BUFFER_SIZE	(4048)
char msg[MSG_BUFFER_SIZE];
int value = 0;

void setup_wifi() {
  delay(10);  
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void Json_Stm32(void) {
 //   StaticJsonDocument<256> doc;
    StaticJsonDocument<2048> doc;
    DeserializationError err = deserializeJson(doc, msg);
    if (!err) {
      String id = doc["id"];
      String command = doc["command"];
      id_coom=id;

      Serial.println();
      Serial.println("Accepted:");
      Serial.println("ID: " + id);
      Serial.println("Command: " + command);
      Serial1.print(command);//UART1 -> stm32
      Serial.println();
    } else {
      Serial.println("Error JSON");
    }
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);  
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    msg[i] =(char)payload[i];
  }
  
  Serial.print(msg);// {"id":"082d0111-ccaf-43ea-9a97-087b6eca31c0","command":"<SN>"}
  Serial.println();
  Json_Stm32();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
   if (client.connect(mqtt_client_id)) {
      Serial.println("connected");
      client.subscribe(">/17:91:a8:06:f4:fc/4243850920/3");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds"); // Wait 5 seconds before retrying     
      delay(5000);
    }
  }
}

void setup() {
  delay(10000);
  
  Serial1.begin(115200, SERIAL_8N1, UART1_RX, UART1_TX); // Аппаратный UART1 -> stm32

  Serial.begin(115200);
  Serial.println("Start Esp32");
  setup_wifi();
  
  espClient.setCACert(root_ca_cert);
  espClient.setCertificate(device_cert);
  espClient.setPrivateKey(private_key);
  client.setServer(mqtt_server, 8883); 
  client.setBufferSize(2048); // Увеличиваем буфер
  client.setKeepAlive(15);           // устанавливает интервал keep-alive для MQTT соединения на 15 секунд.Клиент отправляет PING пакет каждые 15 секунд
  client.setSocketTimeout(30);       // Таймаут TCP сокета
  client.setCallback(callback);
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 2000) {
    lastMsg = now;
    ++value;
    snprintf (msg, MSG_BUFFER_SIZE, "%ld", value);
    client.publish("</17:91:a8:06:f4:fc/4243850920/TestConnectESP32", msg);
  }

   if (Serial1.available()) {   // UART1 <-> stm32
        String response = Serial1.readString();
        Serial.println("");
        Serial.println("response:  ");
        Serial.println(response);
 

        StaticJsonDocument<2048> doc;

        doc["id"] = id_coom;
        doc["result"] = response;

        String jsonStr;
        serializeJson(doc, jsonStr);

        Serial.println("");
        Serial.println("MSG:  ");
 //       Serial.println(jsonStr);  // Отправка по USB 

        snprintf(msg, MSG_BUFFER_SIZE, "%s", jsonStr.c_str());
 //       snprintf(msg, MSG_BUFFER_SIZE, "%s", response.c_str());
         Serial.println(msg);  
        client.publish("</17:91:a8:06:f4:fc/4243850920/3", msg);
/**/
    }

}
