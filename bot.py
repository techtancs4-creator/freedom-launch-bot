
import os
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import discord

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

IST = ZoneInfo("Asia/Kolkata")
LAUNCH_TIME = datetime(2026, 10, 30, 22, 59, tzinfo=IST)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

countdown_task = None


def countdown_text():
    now = datetime.now(IST)
    remaining = LAUNCH_TIME - now

    if remaining.total_seconds() <= 0:
        return None

    total_seconds = int(remaining.total_seconds())
    days, total_seconds = divmod(total_seconds, 86400)
    hours, total_seconds = divmod(total_seconds, 3600)
    minutes, seconds = divmod(total_seconds, 60)

    return (
        "🌍 **FREEDOM SMP — NEW WORLD LOADING!**\n"
        "🚀 Launch countdown is running!\n"
        f"⏳ **{days} days, {hours} hours, "
        f"{minutes} minutes, {seconds} seconds** remaining.\n"
        "✨ *Your world, your rule.*"
    )


async def countdown_loop(channel):
    last_message = None

    while not client.is_closed():
        now = datetime.now(IST)

        if now >= LAUNCH_TIME:
            await channel.send(
                "🚀 **FREEDOM SMP IS NOW LIVE!**\n"
                "🌍 The new world awaits. Join the adventure!\n"
                "✨ Your world, your rule."
            )
            return

        remaining = LAUNCH_TIME - now
        seconds_left = int(remaining.total_seconds())

        # Hourly updates; every minute during the final 10 minutes
        interval = 60 if seconds_left <= 600 else 3600

        message = countdown_text()
        if message and message != last_message:
            await channel.send(message)
            last_message = message

        await asyncio.sleep(min(interval, seconds_left))


@client.event
async def on_ready():
    global countdown_task

    print(f"Logged in as {client.user}")

    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        try:
            channel = await client.fetch_channel(CHANNEL_ID)
        except discord.HTTPException as error:
            print(f"Could not find channel: {error}")
            return

    if not isinstance(channel, discord.VoiceChannel):
        print("CHANNEL_ID must be the voice channel ID.")
        return

    # Join the voice channel if not already connected
    voice_client = discord.utils.get(
        client.voice_clients,
        guild=channel.guild
    )

    if voice_client is None or not voice_client.is_connected():
        try:
            await channel.connect()
        except discord.HTTPException as error:
            print(f"Could not join voice channel: {error}")
            return

    if countdown_task is None or countdown_task.done():
        countdown_task = asyncio.create_task(countdown_loop(channel))


client.run(TOKEN)
