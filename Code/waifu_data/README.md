# 🎨 Waifu Data Storage

## 📁 Struktur Folder
```
waifu_data/
├── images/           # Simpan gambar waifu di sini
│   ├── waifu_1.jpg
│   ├── waifu_2.jpg
│   └── ...
├── metadata.json     # Database metadata waifu
└── README.md         # File ini
```

## 📝 Cara Menambah Waifu Baru

### 1. Tambahkan Gambar
- Simpan gambar waifu di folder `images/`
- Format yang didukung: `.jpg`, `.jpeg`, `.png`, `.gif`
- Beri nama file yang unik (contoh: `waifu_6.jpg`)

### 2. Update Metadata
Buka `metadata.json` dan tambahkan entry baru:

```json
{
  "id": 6,
  "character_name": "Nama Karakter",
  "anime_name": "Nama Anime",
  "image_file": "waifu_6.jpg"
}
```

**Contoh:**
```json
{
  "id": 6,
  "character_name": "Rem",
  "anime_name": "Re:Zero",
  "image_file": "waifu_6.jpg"
}
```

### ⚠️ Penting:
- Pastikan `id` unik dan berurutan
- Pastikan `image_file` sesuai dengan nama file di folder `images/`
- Jangan lupa tambahkan koma (`,`) di akhir entry sebelumnya

## 🎮 Command Bot
Gunakan command `.my` untuk mendapatkan waifu random!
- **Cooldown:** 2 jam per user
- **Format:** `.my`

## 📦 Sample Data
File `metadata.json` sudah berisi 5 contoh waifu:
1. Yor Forger - Spy x Family
2. Marin Kitagawa - My Dress-Up Darling
3. Ai Hoshino - Oshi no Ko
4. Zero Two - Darling in the Franxx
5. Makima - Chainsaw Man

**Catatan:** Gambar untuk sample data perlu ditambahkan secara manual ke folder `images/`



    {
        "id": 13,
        "character_name": "",
        "anime_name": "",
        "image_file": "waifu_13.png"
    },
    {
        "id": 14,
        "character_name": "",
        "anime_name": "",
        "image_file": "waifu_14.png"
    },
    {
        "id": 15,
        "character_name": "",
        "anime_name": "",
        "image_file": "waifu_15.png"
    },
    {
        "id": 16,
        "character_name": "",
        "anime_name": "",
        "image_file": "waifu_16.png"
    },
    {
        "id": 17,
        "character_name": "",
        "anime_name": "",
        "image_file": "waifu_17.png"
    },
    {
        "id": 18,
        "character_name": "",
        "anime_name": "",
        "image_file": "waifu_18.png"
    },
    {
        "id": 19,
        "character_name": "",
        "anime_name": "",
        "image_file": "waifu_19.png"
    },
    {
        "id": 20,
        "character_name": "",
        "anime_name": "",
        "image_file": "waifu_20.png"
    }

        {
        "id": 1,
        "character_name": "Yor Forger",
        "anime_name": "Spy x Family",
        "image_file": "waifu_1.png"
    },
    {
        "id": 2,
        "character_name": "Marin Kitagawa",
        "anime_name": "My Dress-Up Darling",
        "image_file": "waifu_2.png"
    },
    {
        "id": 3,
        "character_name": "Ruri Ichigyou",
        "anime_name": "Hello World",
        "image_file": "waifu_3.png"
    },
    {
        "id": 4,
        "character_name": "Keqing",
        "anime_name": "Genshin Impact",
        "image_file": "waifu_4.png"
    },
    {
        "id": 5,
        "character_name": "Navia",
        "anime_name": "Genshin Impact",
        "image_file": "waifu_5.png"
    },
    {
        "id": 6,
        "character_name": "Sparkle",
        "anime_name": "Honkai: Star Rail",
        "image_file": "waifu_6.png"
    },
    {
        "id": 7,
        "character_name": "Kafka",
        "anime_name": "Honkai: Star Rail",
        "image_file": "waifu_7.png"
    },
    {
        "id": 8,
        "character_name": "Sayu Ogiwara",
        "anime_name": "Higehiro: After Being Rejected, I Shaved and Took in a High School Runaway",
        "image_file": "waifu_8.png"
    },
    {
        "id": 9,
        "character_name": "Gotou Airi",
        "anime_name": "Higehiro: After Being Rejected, I Shaved and Took in a High School Runaway",
        "image_file": "waifu_9.png"
    },
    {
        "id": 10,
        "character_name": "Kiana Kaslana",
        "anime_name": "Honkai Impact 3rd",
        "image_file": "waifu_10.png"
    },