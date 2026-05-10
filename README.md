# 🔐 Smart Lock — Aqlli Kirish Nazorat Tizimi

NFC karta orqali eshikni boshqaruvchi va har bir kirishni bulutda saqlovchi tizim.

![Platform](https://img.shields.io/badge/platform-ESP32-green.svg)
![Backend](https://img.shields.io/badge/backend-Flask-orange.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

---

## 📖 Loyiha haqida

**Smart Lock** — ESP32 mikrokontrolleri va PN532 NFC moduli asosida ishlab chiqilgan aqlli kirish nazorat tizimi. Foydalanuvchi NFC kartasini skanerga yaqinlashtirganida tizim uni tekshiradi, eshikni ochadi va bu voqeani bulut serverida qayd etadi. Admin esa web panel orqali istalgan joydan kirishlarni kuzatib borishi mumkin.


---

## ✨ Asosiy xususiyatlar

- ⚡ NFC karta 0.5 soniyadan kamroq vaqtda o'qiladi
- 🔐 Maxsus 6-baytlik shifrlangan kalit — nusxa olish imkonsiz
- ☁️ Har bir kirish avtomatik bulut serveriga saqlanadi
- 📊 Web panel orqali real vaqtda monitoring (har 5 soniyada yangilanadi)
- 🌐 Bitta server orqali bir nechta eshikni boshqarish mumkin
- 📅 Yil / oy / kun bo'yicha kirish tarixini ko'rish

---

## 🏗 Tizim arxitekturasi

```
[ NFC Karta ]
      │  karta o'qiladi
      ▼
[ ESP32 + PN532 ]  ──▶  [ Rele / Qulf ]
      │                 [ LED 🟢🔴    ]
      │  HTTP POST      [ Buzzer      ]
      ▼
[ Flask Server — PythonAnywhere ]
      │
      ▼
[ SQLite Database ]
      │  GET so'rov
      ▼
[ Web Monitoring Paneli ]
```

---

## 📁 Fayllar

| Fayl | Vazifasi |
|------|----------|
| `Asosiy_akmalvirus_pythonanywhere_com.ino` | ESP32 asosiy kodi — WiFi, NFC o'qish, server bilan aloqa |
| `kartaga_yozish_mifare.ino` | NFC kartaga ism/familiya va ruxsat yozish |
| `63block_tekshirish.ino` | Karta bloklarini tekshirish va debug qilish |
| `Defaultga_qaytarish.ino` | Kartani zavod sozlamalariga qaytarish |
| `server3.py` | Flask backend server + Web monitoring paneli |
| `Smart-Lock.pdf` | Loyiha taqdimoti (PDF) |
| `SmartLock_Loyiha_Tavsifi.docx` | Loyiha tavsifi (Word) |

---

## 🛠 Texnologiyalar

| Qism | Texnologiya |
|------|------------|
| Mikrokontroller | ESP32 |
| NFC moduli | PN532 (SPI, 13.56 MHz) |
| Qurilma dasturi | Arduino C++ |
| Backend | Python Flask |
| Ma'lumotlar bazasi | SQLite |
| Hosting | PythonAnywhere |
| Frontend | HTML / CSS / JavaScript |

---

## 🚀 Ishga tushirish

### Server

```bash
pip install flask flask-cors
python server3.py
```

### ESP32

`Asosiy_akmalvirus_pythonanywhere_com.ino` faylida WiFi va server manzilini o'zgartiring:

```cpp
const char* ssid     = "WIFI_NOMI";
const char* password = "WIFI_PAROLI";
const char* serverUrl = "https://sizning-server.pythonanywhere.com/api/data";
```

Keyin Arduino IDE orqali ESP32 ga yuklang.

### NFC karta tayyorlash

`kartaga_yozish_mifare.ino` ni ishga tushiring va karta bloklariga yozing:

| Blok | Ma'lumot |
|------|----------|
| 4 | Ism (masalan: `Akmal0`) |
| 5 | Familiya (masalan: `Abduraimov0`) |
| 6 | Ruxsat: `1` = kirish bor, `0` = kirish yo'q |

---

## 🏢 Qo'llanish sohalari

- 🏠 Talabalar yotoqxonalari
- 🔬 Universitetlar laboratoriyalari
- 🏢 Ofislar va korxonalar
- 🏫 Maktablar va litseylar
- 🏥 Shifoxona bo'limlari

---
## Videolar:
https://youtube.com/shorts/3wD6ktwxtIk?si=JrrxngOk08a1cbgV    //uzb versiyasi
https://youtube.com/shorts/ixccWTziQWg?si=zYgDLOjXJnUNCZsh    //eng versiyasi


## 👤 Muallif

Abduraimov Akmal TATU KIF 1-kurs talabasi
2026
