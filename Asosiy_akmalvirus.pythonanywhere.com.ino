#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid="WIFINOMI";
const char* password="WIFIPROLI";

const char* serverUrl = "https://Sizningsaytngiz.com/api/data";

#define PN532_SCK  (18)
#define PN532_MOSI (23)
#define PN532_SS   (5)
#define PN532_MISO (19)
#define yashil (2)
#define qizil (4)
#define buzzer (21)
#define rele (13)

Adafruit_PN532 nfc(PN532_SCK,PN532_MISO,PN532_MOSI,PN532_SS);
//bu yerda siz o'rnatgan kalit bo'lishi kerak
uint8_t keya[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid,password);
  Serial.println("Wifiga ulanmoqda...");
  int n=0;
  while(WiFi.status()!=WL_CONNECTED){
    delay(500);
    Serial.print(".");
    if(n>6) break;
    n++;
  }
  
  Serial.println("Salom Xush kelibsiz");

  nfc.begin();

  uint32_t versiondata=nfc.getFirmwareVersion();

  if(!versiondata){
    Serial.print("PN53x boar topilmadi");
    while(1); //cheksiz sikl keyingi qismga o'tmasligi uchun
  }

  nfc.SAMConfig(); //Kartani kutish
  Serial.println("Karta yaqinlashishi kutilmoqda");

  Serial.print("Chip topildi PN5"); Serial.println((versiondata>>24) & 0xFF,HEX);
  Serial.print("Firmvare versiyasi "); Serial.print((versiondata>>16) & 0xFF, DEC);
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);
  
  pinMode(qizil,OUTPUT);
  pinMode(yashil,OUTPUT);
  pinMode(buzzer,OUTPUT);
  pinMode(rele,OUTPUT);

}
void serverga_yubor(String ism, String familiya,String qurilma="ttj3 314-xona"){
  if(WiFi.status()==WL_CONNECTED){
    HTTPClient http;
    http.begin(serverUrl);

    http.setReuse(true);
    http.setTimeout(2000);
    
    http.addHeader("Content-Type","application/json");

    //Json yaratish
    StaticJsonDocument<200> doc;
    doc["ism"]=ism;
    doc["familiya"]=familiya;
    doc["qurilma"]=qurilma;
    
    String jsonOutput;
    serializeJson(doc, jsonOutput);

    //post so'rov yuborish
    int httpResponseCode=http.POST(jsonOutput);

    if(httpResponseCode>0){
      String response=http.getString();
      Serial.println("Server javabi: "+response);
    }
    else{
      Serial.print("Xatolik yuz berdi: ");
      Serial.println(httpResponseCode);
    }
    http.end();

  }
}

void loop() {
  uint8_t success;
  uint8_t uid[]={0,0,0,0,0,0,0,0};
  uint8_t uidLength;

  success=nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if(success){
    Serial.println("Found an ISO14443A card");
    Serial.print("  UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
    Serial.print("  UID Value: ");
    nfc.PrintHex(uid, uidLength);
    Serial.println("");

    success=nfc.mifareclassic_AuthenticateBlock(uid, uidLength, 4, 0, keya);
    if(success){
      Serial.println("kalit tushdi");
      uint8_t data[16];
      success=nfc.mifareclassic_ReadDataBlock(6, data);
      if(success){
        Serial.println(data[0]);
        if(data[0]=='1'){
          //serverga_yubor("Akmal","Abduraimov");
          String ism="",familiya="";
          success=nfc.mifareclassic_ReadDataBlock(4, data);
          int i=0;
          while(data[i]!='0'){
            ism+=(char)data[i];
            i++;
          }
          success=nfc.mifareclassic_ReadDataBlock(5, data);
          int j=0;
          while(data[j]!='0'){
            familiya+=(char)data[j];
            j++;
          }
          
          digitalWrite(rele,HIGH);
          digitalWrite(yashil,HIGH);
          
          digitalWrite(buzzer,HIGH);
          delay(300);
          digitalWrite(buzzer,LOW);
          delay(300);
          digitalWrite(buzzer,HIGH);
          delay(300);
          digitalWrite(yashil,LOW);
          digitalWrite(buzzer,LOW);
          delay(2500);
          digitalWrite(rele,LOW);
          serverga_yubor(ism,familiya);

        }
        else{
          digitalWrite(qizil,HIGH);
          digitalWrite(buzzer,HIGH);
          delay(2000);
          digitalWrite(qizil,LOW);
          digitalWrite(buzzer,LOW);


        }
      }
      else{
        digitalWrite(qizil,HIGH);
        digitalWrite(buzzer,HIGH);
        delay(2000);
        digitalWrite(qizil,LOW);
        digitalWrite(buzzer,LOW);

        }
    }
    else{
      digitalWrite(qizil,HIGH);
      digitalWrite(buzzer,HIGH);
      delay(2000);
      digitalWrite(qizil,LOW);
      digitalWrite(buzzer,LOW);

      }
  }

}
