# Discord → Telegram Mirror

Script buat mirror pesan dari server Discord ke bot Telegram lu, pakai **Discord user token** (akun lu sendiri, bukan bot).

> ⚠️ **WARNING**: Pakai user token (self-bot) **melanggar Discord ToS**. Akun lu bisa kena ban. Resiko ditanggung sendiri.

---

## ✨ Fitur

- ✅ Mirror pesan teks dari Discord ke Telegram
- ✅ Download & forward attachment (foto, video, audio, dokumen) sebagai file beneran, bukan link
- ✅ Support Discord embeds (title, description, fields, image, thumbnail, footer)
- ✅ **Multi-channel** — mirror dari beberapa channel sekaligus
- ✅ **Multi-server** — mirror dari beberapa server sekaligus
- ✅ **Keyword filter** — cuma forward pesan yang mengandung kata tertentu
- ✅ Anti-loop (skip pesan dari akun sendiri secara default)
- ✅ Auto-handle Telegram message limit (4096 char) dengan chunking
- ✅ Fallback link kalau attachment >50MB (limit Telegram bot)

---

## 📦 Yang Lu Butuhkan

| # | Item | Cara Dapat |
|---|---|---|
| 1 | **Discord User Token** | Browser → F12 → Network tab → header `authorization` |
| 2 | **Telegram Bot Token** | Chat [@BotFather](https://t.me/BotFather) → `/newbot` |
| 3 | **Telegram Chat ID** | Chat [@userinfobot](https://t.me/userinfobot) |
| 4 | **Discord Channel/Guild ID** *(opsional)* | Discord Settings → Advanced → Developer Mode ON → klik kanan → Copy ID |

### Cara dapetin Discord User Token

1. Buka [discord.com/app](https://discord.com/app) di browser, login
2. Tekan `F12` (DevTools) → tab **Network**
3. Filter ketik `/api`, lalu refresh halaman
4. Klik request apa aja → tab **Headers** → cari **`authorization`**
5. Copy value-nya (format: `xxxxx.xxxxx.xxxxx`, ~70 char)

### Cara dapetin Telegram Chat ID

**Personal:**
1. Cari bot lu di Telegram → tekan **Start**
2. Buka di browser:
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
3. Cari `"chat":{"id":<ANGKA>}` → itu chat ID lu

**Group:**
1. Invite bot ke group
2. Kirim pesan apa aja di group
3. Cek URL `getUpdates` di atas, chat ID group biasanya negatif (mis. `-1001234567890`)

---

## 🚀 Setup

### 1. Clone & Install

```bash
git clone https://github.com/cheerishbear-spec/mirror.git
cd mirror

# Install pip & venv (skip kalau udah ada)
sudo apt update
sudo apt install -y python3-pip python3-venv

# Bikin virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi

```bash
cp .env.example .env
nano .env       # atau editor favorit lu
```

Isi minimal yang wajib:
```env
DISCORD_TOKEN=MTIzNDU2...
TELEGRAM_BOT_TOKEN=123456789:ABC...
TELEGRAM_CHAT_ID=123456789
```

### 3. Jalankan

```bash
python main.py
```

Notif `✅ Mirror aktif. Login sebagai <username>` bakal masuk ke Telegram lu = berhasil.

---

## ⚙️ Konfigurasi `.env` Lengkap

| Variable | Wajib | Default | Deskripsi |
|---|---|---|---|
| `DISCORD_TOKEN` | ✅ | — | User token akun Discord lu |
| `TELEGRAM_BOT_TOKEN` | ✅ | — | Token bot dari BotFather |
| `TELEGRAM_CHAT_ID` | ✅ | — | ID chat Telegram tujuan |
| `DISCORD_CHANNEL_IDS` | ❌ | (kosong) | Channel ID yang di-mirror, pisah koma |
| `DISCORD_GUILD_IDS` | ❌ | (kosong) | Server ID, dipakai kalau `DISCORD_CHANNEL_IDS` kosong |
| `KEYWORDS` | ❌ | (kosong) | Filter keyword, pisah koma, case-insensitive |
| `MIRROR_SELF` | ❌ | `false` | `true` = pesan akun sendiri juga di-mirror |
| `LOG_LEVEL` | ❌ | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

---

## 📋 Contoh Skenario

### Skenario 1: Mirror semua pesan dari 1 channel
```env
DISCORD_CHANNEL_IDS=1205980077926654063
```

### Skenario 2: Mirror dari beberapa channel sekaligus
```env
DISCORD_CHANNEL_IDS=1229820703662932048,1432258678261547069,971488439931392130
```

### Skenario 3: Mirror semua channel di 1 server
```env
DISCORD_GUILD_IDS=1205980077096050689
```

### Skenario 4: Mirror dari beberapa server sekaligus
```env
DISCORD_GUILD_IDS=1205980077096050689,924442927399313448
```

### Skenario 5: Filter keyword (cuma forward yg ada kata tertentu)
```env
DISCORD_CHANNEL_IDS=1229820703662932048,1432258678261547069
KEYWORDS=airdrop,whitelist,mint,free mint,giveaway
```
→ Cuma pesan yang mengandung salah satu keyword di atas yang akan diforward.  
→ Case-insensitive (`Airdrop`, `AIRDROP`, `airdrop` semua match).  
→ Keyword dicek di teks pesan **dan** isi embed (title, desc, fields).

### Skenario 6: Mirror semuanya tanpa filter
```env
# Kosongin semua filter
DISCORD_CHANNEL_IDS=
DISCORD_GUILD_IDS=
KEYWORDS=
```

---

## 🔄 Tetep Jalan Walaupun SSH Close (VPS)

Pakai **tmux** biar script tetep jalan walaupun terminal ke-close:

```bash
# Install tmux
sudo apt install -y tmux

# Bikin session
tmux new -s mirror

# Di dalam tmux:
source venv/bin/activate
python main.py

# Detach (keluar tanpa mematikan): Ctrl+B, terus tekan D

# Balik kapanpun:
tmux attach -t mirror

# Kill session kalau udah ga butuh:
tmux kill-session -t mirror
```

---

## 🐛 Troubleshooting

### `LoginFailure: Improper token`
Token Discord salah / expired. Ambil ulang lewat DevTools (langkah di atas).

### `Chat not found` di Telegram
Lu belum `/start` bot dari chat tujuan. Buka chat bot di Telegram, kirim `/start`.

### Pesan ga ke-mirror padahal banyak yang chat
1. Cek log startup, harus ada `✅ Channel ... OK` atau `✅ Guild ... OK`
2. Kalau muncul `⚠️  Channel ... NOT FOUND` → channel ID salah / akun lu ga akses
3. Cara cepat dapetin channel ID yang bener:
   - Buka [discord.com/app](https://discord.com/app) → klik channel target
   - URL nya: `https://discord.com/channels/GUILD_ID/CHANNEL_ID`
   - Angka pertama = guild ID, angka kedua = channel ID

### `ModuleNotFoundError: No module named 'discord'`
Belum install dependencies. Jalanin:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### `pip: command not found`
Install dulu:
```bash
sudo apt install -y python3-pip python3-venv
```

### `python: command not found` (di Ubuntu)
Pakai `python3` atau aktifin venv dulu (`source venv/bin/activate`).

### Akun Discord logout tiba-tiba
Kemungkinan kena detect self-bot. Hindari:
- Login paralel di banyak tempat
- Spam-heavy channel
- Pakai VPS dengan IP datacenter yang aneh

---

## 💡 Tips Biar Aman

- **Jangan commit `.env`** ke git (udah di-handle `.gitignore`)
- **Jangan share token** ke siapapun
- **Ganti password Discord = token expired** otomatis
- Pakai akun Discord khusus (bukan akun utama lu) buat self-bot
- Mulai test di server kecil dulu sebelum production

---

## 📁 Struktur File

```
mirror/
├── main.py            # Script utama
├── requirements.txt   # Python dependencies
├── .env.example       # Template env (aman di-commit)
├── .env               # Token & config lu (JANGAN commit!)
├── .gitignore         # Exclude .env, venv/, dll
└── README.md          # Dokumentasi (file ini)
```

---

## 📜 License

Use at your own risk. Author ga bertanggung jawab atas akun yang ke-ban karena pakai script ini.
