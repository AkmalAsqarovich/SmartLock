#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

#define PN532_SCK  (18)
#define PN532_MOSI (23)
#define PN532_SS   (5)
#define PN532_MISO (19)


Adafruit_PN532 nfc(PN532_SCK,PN532_MISO,PN532_MOSI,PN532_SS);

void setup() {
  Serial.begin(115200);
  while(!Serial) delay(10);
  Serial.println("Salom xush kelibsiz");

  nfc.begin();

  uint32_t versiondata=nfc.getFirmwareVersion();

  if(!versiondata){
    Serial.print("PN53x boar topilmadi");
    while(1); //cheksiz sikl keyingi qismga o'tmasligi uchun
  }
  nfc.SAMConfig(); ////KArtani kutish
  Serial.println("Karta yaqinlashishi kutilmoqda");

  Serial.print("Chip topildi PN5"); Serial.println((versiondata>>24) & 0xFF,HEX);
  Serial.print("Firmvare versiyasi "); Serial.println((versiondata>>16) & 0xFF, DEC);
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);

  

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

    if(uidLength==4){
      Serial.println("Klassik 4byteli mifare karta");
      uint8_t keya[6]= { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };
      uint8_t keyb[6]={ 0xXX 0xXX, 0xXX, 0xXX, 0xXX, 0xXX };    ///Key B

      success=nfc.mifareclassic_AuthenticateBlock(uid, uidLength, 4, 1, keyb);

      if(success){
        Serial.println("Karta avval sozlangan");
        uint8_t block4Data[16] = {'A','k','m','a','l','b','e','k','-','t','a','t','u','1','1','1'};
        if(nfc.mifareclassic_WriteDataBlock(6, block4Data)){
          Serial.println("6-blockga malumot yozildi ");
        }
      }
      else{
        Serial.println("Karta yangi uning B keyini almashtiramiz........");
        success=nfc.mifareclassic_AuthenticateBlock(uid, uidLength, 7, 0, keya);
        if(success){

          uint8_t block7Data[16]={
            0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,  //Key A
            0x78, 0x77, 0x88, 0x69,              //Acces bits  787788
            0xXX, 0xXX, 0xXX, 0xXX, 0xXX, 0xXX   //Key B
          };

          if(nfc.mifareclassic_WriteDataBlock(7, block7Data)){
            Serial.println("Karta sozlandi uni qaytadan tekkissangiz malumot yoziladi");
          }

        }
        else{
          Serial.println("Kalitlar tushmadi");
        }
      }
    }
    
    else{
      Serial.println("Xatolik kelib chiqdi boshqa kartadan foydalaning!");
    }
    delay(4000);

  }

  else{
    Serial.println("Xatolik kelib chiqdi!");
  }
  delay(500);

}
