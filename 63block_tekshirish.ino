#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

#define PN532_SCK  (18)
#define PN532_MOSI (23)
#define PN532_SS   (5)
#define PN532_MISO (19)

Adafruit_PN532 nfc(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);

void setup(void) {
  Serial.begin(115200);
  while (!Serial) delay(10); 

  Serial.println("Hello!");

  nfc.begin();

  uint32_t versiondata = nfc.getFirmwareVersion();
  if (! versiondata) {
    Serial.print("Didn't find PN53x board");
    while (1); // halt
  }
  // Got ok data, print it out!
  Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX);
  Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC);
  Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);

  Serial.println("Waiting for an ISO14443A Card ...");
}


void loop(void) {
  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 }; 
  uint8_t uidLength;                       
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success) {
    Serial.println("Found an ISO14443A card");
    Serial.print("  UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
    Serial.print("  UID Value: ");
    nfc.PrintHex(uid, uidLength);
    Serial.println("");

    if (uidLength == 4){
      Serial.println("Klassik mifare karta");

      uint8_t keya[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF }; // o'qish uchun default kalit yoki 

      for(int i=0;i<16;i++){
        success=nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
        success=nfc.mifareclassic_AuthenticateBlock(uid, uidLength, i*4, 0, keya);
        Serial.print("[-----------------------------------------");

        Serial.print(i);

        Serial.println("----------------------------------------]");

        if(success){
          uint8_t data[16];
          success=nfc.mifareclassic_ReadDataBlock(i*4,data);
          Serial.print(i*4);
          Serial.print("]");
          nfc.PrintHex(data, 16);

          success=nfc.mifareclassic_ReadDataBlock(i*4+1,data);
          Serial.print(i*4+1);
          Serial.print("]");
          nfc.PrintHex(data, 16);

          success=nfc.mifareclassic_ReadDataBlock(i*4+2,data);
          Serial.print(i*4+2);
          Serial.print("]");
          nfc.PrintHex(data, 16);

          success=nfc.mifareclassic_ReadDataBlock(i*4+3,data);
          Serial.print(i*4+3);
          Serial.print("]");
          nfc.PrintHex(data, 16);

          
        }
        
        else{
          ///
        }
        
      }
      delay(2000);
    }
  }
  else{
    Serial.println("Default kalit tushmadi");
  }
}

