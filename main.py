import datetime
import json
import os

import discord
from dotenv import load_dotenv

load_dotenv()
bot = discord.Client()

STATE_FILE = "state.json"
with open(STATE_FILE, "w") as f:
    f.write("{}")


# Util: Load and save state
def load_state():
    with open(STATE_FILE, "w") as f:
        json.dump({}, f)
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


global statuses
statuses = {
    "online": "I am most likely available to chat",
    "idle": "I'm AFK, I'll respond later",
    "dnd": "Really busy, won't respond.",
    "offline": "Sleeping or just gone",
}


async def get_state():
    global statuses
    return json.dumps(
        {"status": str(bot.status).capitalize(), "means": statuses[str(bot.status)]},
        indent=2,
    )


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return

    if isinstance(message.channel, discord.DMChannel):
        state = load_state()
        author_id = str(message.author.id)  # keys must be strings for JSON

        now_ts = int(datetime.datetime.now().timestamp())
        cooldown_ts = state.get(author_id, 0)

        if now_ts < cooldown_ts + 300:
            return

        state[author_id] = now_ts
        save_state(state)

        print(f"📬 DM from {message.author.name}")
        # await message.unack()
        state = await get_state()
        await message.channel.send(
            f"-# (automated message)\nHey, thanks for the message! — I'm currently:\n\n```json\n{state}```\nHeres what my other statuses usually mean:\n\n```json\n{json.dumps(statuses,indent=2)}```\nThanks for reaching out and I'll respond as soon as i can!\n— Spelis"
        )


bot.run(os.getenv("TOKEN", ""))
