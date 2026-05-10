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



}

void loop() {
  uint8_t success;
  uint8_t uid[]={0,0,0,0,0,0,0,0};
  uint8_t uidLength;

  success=nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
  if(success){

  uint8_t keyb[6]={0xXX, 0xXX, 0xXX, 0xXX, 0xXX, 0xXX}; // bu yerda siz o'rnatgan maxfiy B kalit bo'lishi kerak

  uint8_t block7Data[16]={
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0x07, 0x80, 0x69,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF        /// bu yerda default holatga qaytariladigan sector trailer datasni yozilgan
  };

  Serial.println("Key b bilan kirishga urinilayabdi.....");

  success=nfc.mifareclassic_AuthenticateBlock(uid,uidLength,7,1,keyb);

  if(success){
    if(nfc.mifareclassic_WriteDataBlock(7,block7Data)){
      Serial.println("Karta default holatga qaytarildi");
      Serial.println("key A ham key B ham F");
      uint8_t block4Data[16] = {'0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'};   ///ism
        uint8_t block5Data[16] = {'0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'};   ///familiya
        uint8_t block6Data[16] = {'0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'};   ///ruxsat darajasi
        if(nfc.mifareclassic_WriteDataBlock(4, block4Data)){
          uint8_t *data= new uint8_t[16];
          success=nfc.mifareclassic_ReadDataBlock(4, data);
          Serial.print("4]");
          nfc.PrintHex(data, 16);

          Serial.println("Ism muvaffaqiyatli defaultga qaytarildi...");
          
          if(nfc.mifareclassic_WriteDataBlock(5, block5Data)){
            success=nfc.mifareclassic_ReadDataBlock(5, data);
            Serial.print("5]");
            nfc.PrintHex(data, 16);

            Serial.println("Familiya muvaffaqiyatli defaultga qaytarildi...");

            if(nfc.mifareclassic_WriteDataBlock(6, block6Data)){
              success=nfc.mifareclassic_ReadDataBlock(6, data);
              Serial.print("6]");
              nfc.PrintHex(data, 16);
              Serial.println("Ruxsat darajasi muvaffaqiyatli defaultga qaytarildi...");
            }
            else{
              Serial.println("Ruxsat darajasi xatolik...");
            }
          }
          else{
            Serial.println("Familiya xatolik...");
          }
          delete[] data;
        }
        else{
          Serial.println("Ismxatolik...");
        }
    }
    else{
      Serial.println("Yozishda xatolik kelib chiqdi");
    }

  }
  else{
    Serial.println("Key B xato! Yoki allaqachon defaultga qaytarilgan .......");
  }
  delay(2000);


}
}
