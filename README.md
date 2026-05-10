# 🔐 Smart Lock — Aqlli Kirish Nazorat Tizimi

> NFC karta orqali eshikni boshqaruvchi, har bir kirishni bulutda saqlovchi va real vaqtda monitoring qilish imkonini beruvchi innovatsion tizim.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-ESP32-green.svg)
![Backend](https://img.shields.io/badge/backend-Flask-orange.svg)
![Database](https://img.shields.io/badge/database-SQLite-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

---

## 📋 Mundarija

- [Loyiha haqida](#-loyiha-haqida)
- [Muammo va yechim](#-muammo-va-yechim)
- [Xususiyatlar](#-xususiyatlar)
- [Tizim arxitekturasi](#-tizim-arxitekturasi)
- [Texnologiyalar](#-texnologiyalar)
- [O'rnatish va ishga tushirish](#-ornatish-va-ishga-tushirish)
- [API hujjatlari](#-api-hujjatlari)
- [Papka tuzilmasi](#-papka-tuzilmasi)
- [Qo'llanish sohalari](#-qollanish-sohalari)
- [Muallif](#-muallif)

---

## 📖 Loyiha haqida

**Smart Lock** — bu ESP32 mikrokontrolleri va PN532 NFC moduli asosida qurilgan aqlli kirish nazorat tizimi. Tizim foydalanuvchi NFC kartasini skanerga yaqinlashtirganida uni tekshirib, eshikni ochadi va bu voqeani bulut serverida qayd etadi.

Loyiha **TATU "Eng yaxshi oliy ta'lim ixtirochisi"** respublika tanlovida **Sun'iy intellekt va IT** yo'nalishi bo'yicha taqdim etilgan.

---

## 🔍 Muammo va yechim

### Muammo
Ko'plab ta'lim muassasalari va yotoqxonalarda an'anaviy mexanik kalit tizimi qo'llaniladi:
- Kalit yo'qolishi yoki nusxa olinishi — xavfsizlik tahdidi
- Kim qachon kirganini kuzatib bo'lmaydi
- Ruxsatsiz kirishni aniqlash imkoni yo'q
- Ko'p xona uchun kalit boshqaruvi qiyin va qimmat

### Yechim
Maxsus shifrlangan NFC karta + bulut server + real vaqt web monitoring paneli.

---

## ✨ Xususiyatlar

- ⚡ **Tezkor kirish** — NFC karta 0.5 soniyadan kamroq vaqtda o'qiladi
- 🔐 **Xavfsiz shifrlash** — maxsus 6-baytlik kalit (standart kartalarni o'qib bo'lmaydi)
- ☁️ **Bulut saqlash** — har bir kirish avtomatik SQLite bazaga saqlanadi
- 📊 **Real vaqt monitoring** — web panel har 5 soniyada yangilanadi
- 🌐 **Ko'p qurilmali** — bitta server orqali cheksiz eshikni boshqarish
- 🟢🔴 **Vizual signallar** — yashil/qizil LED va buzzer orqali tezkor javob
- 📅 **Kalendar ko'rinishi** — yil/oy/kun bo'yicha kirish tarixini ko'rish
- 🔗 **Ochiq REST API** — boshqa tizimlar bilan integratsiya imkoni

---

## 🏗 Tizim arxitekturasi

```
┌─────────────────────────────────────────────────────────┐
│                    FOYDALANUVCHI                         │
│                  [ NFC Karta ]                           │
└───────────────────────┬─────────────────────────────────┘
                        │ Karta skanlanadi (13.56 MHz)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  QURILMA QATLAMI                         │
│                                                          │
│   ┌──────────────┐      ┌──────────────────────────┐    │
│   │  PN532 NFC   │─────▶│   ESP32 Mikrokontroller  │    │
│   │   Moduli     │      │   (Arduino C++ kodi)     │    │
│   └──────────────┘      └──────┬───────────────────┘    │
│                                │                         │
│              ┌─────────────────┼──────────────┐         │
│              ▼                 ▼              ▼          │
│          [Rele]            [LED 🟢🔴]      [Buzzer]     │
│          [Qulf]                                          │
└────────────────────────────────┬────────────────────────┘
                                 │ HTTP POST (JSON)
                                 │ WiFi orqali
                                 ▼
┌─────────────────────────────────────────────────────────┐
│                  SERVER QATLAMI                          │
│                                                          │
│   ┌─────────────────────┐   ┌──────────────────────┐   │
│   │   Flask REST API    │──▶│   SQLite Database    │   │
│   │  (PythonAnywhere)   │   │  records / devices   │   │
│   └─────────────────────┘   └──────────────────────┘   │
└────────────────────────────────┬────────────────────────┘
                                 │ GET /api/records
                                 ▼
┌─────────────────────────────────────────────────────────┐
│                  ADMIN QATLAMI                           │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │         Web Monitoring Paneli                   │   │
│   │   Dashboard · Kalendar · Qurilmalar · Tarix    │   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠 Texnologiyalar

| Qism | Texnologiya | Versiya |
|------|------------|---------|
| Mikrokontroller | ESP32 | — |
| NFC moduli | PN532 (SPI) | — |
| Qurilma dasturi | Arduino (C++) | 2.x |
| Backend | Python Flask | 3.x |
| Ma'lumotlar bazasi | SQLite | 3.x |
| Hosting | PythonAnywhere | — |
| Frontend | HTML / CSS / JavaScript | — |
| Kutubxona (NFC) | Adafruit PN532 | 1.x |
| Kutubxona (JSON) | ArduinoJson | 6.x |

---

## 🚀 O'rnatish va ishga tushirish

### Talablar

- ESP32 devkit
- PN532 NFC moduli
- Python 3.8+
- Arduino IDE 2.x

### 1. Repositoryni klonlash

```bash
git clone https://github.com/username/smart-lock.git
cd smart-lock
```

### 2. Server o'rnatish

```bash
cd server

# Kutubxonalarni o'rnatish
pip install flask flask-cors

# Serverni ishga tushirish
python server.py
```

Server `http://localhost:5000` da ishga tushadi.

### 3. ESP32 sozlash

`arduino/main.ino` faylida quyidagi qatorlarni o'zgartiring:

```cpp
const char* ssid     = "SIZNING_WIFI_NOMI";
const char* password = "SIZNING_WIFI_PAROLI";

const char* serverUrl = "https://sizning-server.pythonanywhere.com/api/data";
```

### 4. NFC karta sozlash

Kartaning 4-blokiga ruxsat belgisini yozing (`'1'` — ruxsat bor, `'0'` — ruxsat yo'q):

| Blok | Mazmun |
|------|--------|
| 4 | Ism (masalan: `Akmal0`) |
| 5 | Familiya (masalan: `Abduraimov0`) |
| 6 | Ruxsat belgisi (`1` yoki `0`) |

### 5. Arduino IDE ga yuklash

1. `arduino/main.ino` faylini Arduino IDE da oching
2. Kerakli kutubxonalarni o'rnating:
   - `Adafruit PN532`
   - `ArduinoJson`
   - `WiFi` (ESP32 bilan birga keladi)
3. Board: `ESP32 Dev Module` ni tanlang
4. Upload tugmasini bosing

---

## 📡 API hujjatlari

### Kirish ma'lumotini yuborish

```http
POST /api/data
Content-Type: application/json
```

**So'rov:**
```json
{
  "ism": "Akmal",
  "familiya": "Abduraimov",
  "qurilma": "yotoqxona-314-xona"
}
```

**Javob:**
```json
{
  "status": "ok",
  "xabar": "Ma'lumot saqlandi"
}
```

---

### Barcha yozuvlarni olish

```http
GET /api/records
```

**Javob:**
```json
[
  {
    "id": 1,
    "ism": "Akmal",
    "familiya": "Abduraimov",
    "qurilma": "yotoqxona-314-xona",
    "vaqt": "09:35:12",
    "sana": "10.05.2026",
    "timestamp": "2026-05-10T09:35:12"
  }
]
```

---

### Qurilmalar ro'yxati

```http
GET /api/devices
```

```http
POST /api/devices
Content-Type: application/json

{
  "qurilma_nomi": "lab-101",
  "joylashuv": "1-bino, 1-qavat"
}
```

---

## 📁 Papka tuzilmasi

```
smart-lock/
│
├── arduino/
│   └── main.ino              # ESP32 asosiy kod
│
├── server/
│   └── server.py             # Flask backend + web panel
│
├── docs/
│   ├── SmartLock_Tavsif.docx # Loyiha tavsifi (Word)
│   └── SmartLock_Taqdimot.pptx # Taqdimot (PowerPoint)
│
├── .gitignore
└── README.md
```

---

## 🏢 Qo'llanish sohalari

| Soha | Foyda |
|------|-------|
| 🏠 Yotoqxonalar | Xona kirish nazorati, davomat hisobi |
| 🔬 Laboratoriyalar | Ruxsatsiz kirishni oldini olish |
| 🏢 Ofislar | Xodimlar kirishini nazorat qilish |
| 🏥 Shifoxonalar | Bo'lim kirish boshqaruvi |
| 🏫 Maktablar | O'quvchi davomat tizimi |

---

## 👤 Muallif

**TATU — Toshkent Axborot Texnologiyalari Universiteti**

- Tanlov: *"Eng yaxshi oliy ta'lim ixtirochisi"* — Respublika bosqichi, 2026
- Yo'nalish: Sun'iy intellekt va IT

---

## 📄 Litsenziya

Bu loyiha [MIT](LICENSE) litsenziyasi ostida tarqatilgan.
