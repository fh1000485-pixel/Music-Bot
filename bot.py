import os
import subprocess

from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import MediaStream, AudioQuality

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
SESSION_STRING = os.environ["SESSION_STRING"]

# Bot account — commands handle karega
bot = Client(
    "MusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# User account — voice chat join karega
user = Client(
    "MusicAssistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

call = PyTgCalls(user)


@bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "🎵 **Music Bot Ready!**\n\n"
        "▶️ `/play Song Name`\n"
        "⏸ `/pause`\n"
        "▶️ `/resume`\n"
        "⏹ `/stop`"
    )


@bot.on_message(filters.command("play"))
async def play(_, message):

    if len(message.command) < 2:
        await message.reply_text("❌ Example: `/play Believer`")
        return

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔎 Searching **{query}**..."
    )

    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--default-search",
                "ytsearch1",
                "--get-id",
                "--no-warnings",
                f"ytsearch1:{query}"
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        lines = result.stdout.strip().splitlines()

        if not lines:
            await msg.edit_text("❌ Song nahi mili.")
            return

        video_id = lines[-1]
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"

        # Direct audio URL nikalo
        audio = subprocess.run(
            [
                "yt-dlp",
                "-f",
                "bestaudio",
                "--get-url",
                "--no-warnings",
                youtube_url
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        audio_url = audio.stdout.strip().splitlines()[0]

        call.play(
            message.chat.id,
            MediaStream(
                audio_url,
                audio_parameters=AudioQuality.HIGH
            )
        )

        await msg.edit_text(
            f"🎵 **Now Playing:**\n{query}"
        )

    except Exception as e:
        await msg.edit_text(
            f"❌ **Error:**\n`{str(e)[:1000]}`"
        )


@bot.on_message(filters.command("pause"))
async def pause(_, message):
    try:
        call.pause(message.chat.id)
        await message.reply_text("⏸ **Paused**")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


@bot.on_message(filters.command("resume"))
async def resume(_, message):
    try:
        call.resume(message.chat.id)
        await message.reply_text("▶️ **Resumed**")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


@bot.on_message(filters.command("stop"))
async def stop(_, message):
    try:
        call.leave_call(message.chat.id)
        await message.reply_text("⏹ **Stopped**")
    except Exception as e:
        await message.reply_text(f"❌ `{e}`")


print("🚀 Starting Music Bot...")

bot.start()
user.start()
call.start()

print("✅ Music Bot Started!")

idle()
