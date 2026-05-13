"""
Discord to Telegram Mirror
---------------------------
Mirror pesan dari server Discord (pakai user token / self-bot) ke Telegram bot.

Fitur:
- Mirror pesan teks
- Download & forward attachment (photo / video / audio / document)
- Support Discord embeds (title, description, fields, images, thumbnail)
- Filter by channel ID atau guild (server) ID

PERINGATAN:
Script ini menggunakan Discord USER TOKEN (self-bot), yang MELANGGAR
Discord Terms of Service. Akun Discord Anda berisiko di-ban.
Gunakan dengan risiko sendiri.
"""

import asyncio
import io
import logging
import os
import sys
from typing import Optional, Set

import aiohttp
import discord  # discord.py-self
from dotenv import load_dotenv
from telegram import Bot, InputFile
from telegram.constants import ParseMode
from telegram.error import TelegramError

# --- Load environment --------------------------------------------------------
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

_raw_channels = os.getenv("DISCORD_CHANNEL_IDS", "").strip()
MIRROR_CHANNEL_IDS: Set[int] = (
    {int(cid.strip()) for cid in _raw_channels.split(",") if cid.strip()}
    if _raw_channels
    else set()
)

_raw_guilds = os.getenv("DISCORD_GUILD_IDS", "").strip()
MIRROR_GUILD_IDS: Set[int] = (
    {int(gid.strip()) for gid in _raw_guilds.split(",") if gid.strip()}
    if _raw_guilds
    else set()
)

# Telegram limit untuk upload via bot: 50 MB. Kalau lebih, fallback ke link.
MAX_UPLOAD_BYTES = 50 * 1024 * 1024

# --- Validate ----------------------------------------------------------------
missing = [
    name
    for name, val in [
        ("DISCORD_TOKEN", DISCORD_TOKEN),
        ("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN),
        ("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID),
    ]
    if not val
]
if missing:
    print(f"[ERROR] Env variable tidak lengkap: {', '.join(missing)}")
    print("Copy .env.example ke .env lalu isi dulu.")
    sys.exit(1)

# --- Logging -----------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("mirror")

# --- Telegram bot ------------------------------------------------------------
tg_bot = Bot(token=TELEGRAM_BOT_TOKEN)

# --- Helpers -----------------------------------------------------------------

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv"}
AUDIO_EXTS = {".mp3", ".ogg", ".wav", ".m4a", ".flac"}


def escape_md(text: Optional[str]) -> str:
    """Escape karakter spesial MarkdownV2 Telegram."""
    if not text:
        return ""
    specials = r"_*[]()~`>#+-=|{}.!\\"
    return "".join(f"\\{c}" if c in specials else c for c in text)


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


async def send_text(text: str) -> None:
    """Kirim teks ke Telegram, handle limit 4096 char dengan chunking."""
    if not text:
        return
    # Telegram hard limit: 4096 char per message
    CHUNK = 4000
    for i in range(0, len(text), CHUNK):
        try:
            await tg_bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=text[i : i + CHUNK],
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=False,
            )
        except TelegramError as e:
            log.error("Gagal kirim teks ke Telegram: %s", e)


async def download_attachment(
    session: aiohttp.ClientSession, url: str
) -> Optional[bytes]:
    """Download attachment dari Discord CDN. Return None kalau gagal / too big."""
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                log.warning("Download gagal (%s) untuk %s", resp.status, url)
                return None
            # Cek Content-Length dulu biar ga buang bandwidth
            size = int(resp.headers.get("Content-Length") or 0)
            if size and size > MAX_UPLOAD_BYTES:
                log.info("File kegedean (%s bytes), skip upload", size)
                return None
            data = await resp.read()
            if len(data) > MAX_UPLOAD_BYTES:
                return None
            return data
    except Exception as e:
        log.error("Error download %s: %s", url, e)
        return None


async def send_attachment(
    session: aiohttp.ClientSession,
    attachment: discord.Attachment,
    caption: Optional[str] = None,
) -> None:
    """Download attachment dari Discord lalu kirim ke Telegram dengan tipe yang sesuai."""
    filename = attachment.filename
    ext = os.path.splitext(filename)[1].lower()
    url = attachment.url

    data = await download_attachment(session, url)

    # Fallback: kalau gagal download / kegedean, kirim link aja
    if data is None:
        fallback = (
            f"📎 Attachment \\(ga bisa di\\-upload, kegedean/gagal\\): "
            f"[{escape_md(filename)}]({escape_md(url)})"
        )
        await send_text(fallback)
        return

    buf = io.BytesIO(data)
    buf.name = filename
    tg_caption = caption[:1024] if caption else None

    try:
        if ext in IMAGE_EXTS and ext != ".gif":
            await tg_bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=InputFile(buf, filename=filename),
                caption=tg_caption,
                parse_mode=ParseMode.MARKDOWN_V2 if tg_caption else None,
            )
        elif ext == ".gif":
            await tg_bot.send_animation(
                chat_id=TELEGRAM_CHAT_ID,
                animation=InputFile(buf, filename=filename),
                caption=tg_caption,
                parse_mode=ParseMode.MARKDOWN_V2 if tg_caption else None,
            )
        elif ext in VIDEO_EXTS:
            await tg_bot.send_video(
                chat_id=TELEGRAM_CHAT_ID,
                video=InputFile(buf, filename=filename),
                caption=tg_caption,
                parse_mode=ParseMode.MARKDOWN_V2 if tg_caption else None,
            )
        elif ext in AUDIO_EXTS:
            await tg_bot.send_audio(
                chat_id=TELEGRAM_CHAT_ID,
                audio=InputFile(buf, filename=filename),
                caption=tg_caption,
                parse_mode=ParseMode.MARKDOWN_V2 if tg_caption else None,
            )
        else:
            await tg_bot.send_document(
                chat_id=TELEGRAM_CHAT_ID,
                document=InputFile(buf, filename=filename),
                caption=tg_caption,
                parse_mode=ParseMode.MARKDOWN_V2 if tg_caption else None,
            )
    except TelegramError as e:
        log.error("Gagal kirim attachment %s: %s", filename, e)
        # Fallback ke link
        await send_text(
            f"📎 Attachment \\(gagal upload\\): "
            f"[{escape_md(filename)}]({escape_md(url)})"
        )


def format_embed(embed: discord.Embed) -> str:
    """Format Discord embed jadi teks MarkdownV2 Telegram."""
    parts = ["┌─ *Embed*"]

    if embed.author and embed.author.name:
        parts.append(f"👤 {escape_md(embed.author.name)}")

    if embed.title:
        if embed.url:
            parts.append(f"*[{escape_md(embed.title)}]({escape_md(embed.url)})*")
        else:
            parts.append(f"*{escape_md(embed.title)}*")

    if embed.description:
        parts.append(escape_md(truncate(embed.description, 1500)))

    for field in embed.fields:
        name = escape_md(field.name or "")
        value = escape_md(truncate(field.value or "", 500))
        parts.append(f"• *{name}*\n{value}")

    if embed.image and embed.image.url:
        parts.append(f"🖼 [image]({escape_md(embed.image.url)})")
    if embed.thumbnail and embed.thumbnail.url:
        parts.append(f"🖼 [thumbnail]({escape_md(embed.thumbnail.url)})")

    if embed.footer and embed.footer.text:
        parts.append(f"_{escape_md(embed.footer.text)}_")

    parts.append("└─")
    return "\n".join(parts)


# --- Discord client ----------------------------------------------------------
client = discord.Client()


def should_mirror(message: discord.Message) -> bool:
    """Cek apakah pesan ini termasuk yang mau di-mirror."""
    if message.author.id == client.user.id:
        return False
    if MIRROR_CHANNEL_IDS:
        return message.channel.id in MIRROR_CHANNEL_IDS
    if MIRROR_GUILD_IDS:
        guild = getattr(message, "guild", None)
        return guild is not None and guild.id in MIRROR_GUILD_IDS
    return True


@client.event
async def on_ready():
    log.info("Logged in as %s (id=%s)", client.user, client.user.id)
    log.info(
        "Filter: channels=%s, guilds=%s",
        MIRROR_CHANNEL_IDS or "ALL",
        MIRROR_GUILD_IDS or "ALL",
    )
    try:
        await tg_bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"✅ Mirror aktif\\. Login sebagai `{escape_md(str(client.user))}`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    except TelegramError as e:
        log.warning("Ga bisa kirim notif start: %s", e)


@client.event
async def on_message(message: discord.Message):
    if not should_mirror(message):
        return

    guild_name = message.guild.name if message.guild else "DM"
    channel_name = getattr(message.channel, "name", "direct-message")
    author = str(message.author)
    content = message.content or ""

    # --- Header + body text ---
    header = (
        f"*{escape_md(guild_name)}* \\| *\\#{escape_md(channel_name)}*\n"
        f"👤 *{escape_md(author)}*"
    )
    body = f"\n\n{escape_md(content)}" if content else ""
    text = header + body

    # --- Embeds ---
    if message.embeds:
        embed_blocks = [format_embed(e) for e in message.embeds]
        text += "\n\n" + "\n\n".join(embed_blocks)

    await send_text(text)

    # --- Attachments (download & forward) ---
    if message.attachments:
        async with aiohttp.ClientSession() as session:
            for att in message.attachments:
                await send_attachment(session, att)


async def main():
    try:
        await client.start(DISCORD_TOKEN)
    except discord.LoginFailure:
        log.error("Login Discord gagal. Cek DISCORD_TOKEN lu.")
    except KeyboardInterrupt:
        log.info("Stopping...")
    finally:
        if not client.is_closed():
            await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBye 👋")
