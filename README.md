# Discord → Telegram Mirror

Script buat mirror pesan dari server Discord ke bot Telegram lu, pakai **Discord user token** (akun lu sendiri, bukan bot).

> ⚠️ **WARNING**: Pakai user token (self-bot) **melanggar Discord ToS**. Akun lu bisa kena ban. Resiko ditanggung sendiri.

## Fitur

- Listen pesan dari channel/server yang lu pilih
- Forward teks ke chat/group Telegram
- Kirim link attachment (gambar/file) ke Telegram
- Filter by channel ID atau guild (server) ID

## Yang Lu Butuhkan

1. **Discord user token**
   - Buka Discord di browser
   - Tekan `F12` → tab **Network**
   - Refresh halaman, klik request apa aja
   - Cari header `authorization` → copy value-nya
2. **Telegram bot token** — chat [@BotFather](https://t.me/BotFather) → `/newbot`
3. **Telegram chat ID** — chat [@userinfobot](https://t.me/userinfobot)
   - Kalau target-nya group: masukin bot ke group, lalu kirim `/start`, cek via `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. **Discord channel ID** (opsional)
   - Discord Settings → Advanced → aktifkan **Developer Mode**
   - Klik kanan channel → **Copy Channel ID**

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy env template & isi
cp .env.example .env
# edit .env pakai editor favorit lu

# 3. Run
python main.py
```

## Konfigurasi `.env`

| Variable | Wajib | Deskripsi |
|---|---|---|
| `DISCORD_TOKEN` | ✅ | User token akun Discord lu |
| `TELEGRAM_BOT_TOKEN` | ✅ | Token bot dari BotFather |
| `TELEGRAM_CHAT_ID` | ✅ | ID chat Telegram tujuan |
| `DISCORD_CHANNEL_IDS` | ❌ | Channel ID yang di-mirror (pisah koma). Kosong = semua |
| `DISCORD_GUILD_IDS` | ❌ | Server ID (pisah koma). Dipakai kalau `DISCORD_CHANNEL_IDS` kosong |

## Troubleshooting

- **`LoginFailure`** → token Discord salah/expired. Ambil ulang.
- **Chat not found** di Telegram → lu belum pernah `/start` bot dari chat tujuan.
- **Pesan ga ke-mirror** → cek filter `DISCORD_CHANNEL_IDS` / `DISCORD_GUILD_IDS`.
- **Akun Discord logout tiba-tiba** → kemungkinan kena detect self-bot. Hati-hati.

## Tips Biar Ga Gampang Kedetect

- Jangan mirror spam-heavy channel
- Jangan login paralel di banyak tempat
- Jangan react/kirim pesan otomatis (script ini cuma baca)
- Pakai VPS yang IP-nya ga aneh
