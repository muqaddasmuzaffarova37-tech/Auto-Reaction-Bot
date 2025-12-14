import os
import json
from datetime import date
from pyrogram import Client, filters
from pyrogram.types import ReactionTypeEmoji

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"posts": {}, "admins": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

app = Client(
    "auto_react_bot",
    bot_token=BOT_TOKEN
)

@app.on_message(filters.channel & filters.chat(CHANNEL_ID))
def collect_posts(client, message):
    today = str(date.today())
    data = load_data()
    data["posts"].setdefault(today, [])
    if message.id not in data["posts"][today]:
        data["posts"][today].append(message.id)
        save_data(data)

@app.on_message(filters.private & filters.command("setreactions"))
def set_reactions(client, message):
    if not message.from_user:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        message.reply("❗ 15 ta emoji vergul bilan yuboring")
        return

    emojis = [e.strip() for e in parts[1].split(",") if e.strip()]

    if len(emojis) != 15:
        message.reply("❗ Aynan 15 ta emoji bo‘lishi shart")
        return

    today = str(date.today())
    data = load_data()
    data["admins"].setdefault(today, {})
    data["admins"][today][str(message.from_user.id)] = emojis
    save_data(data)

    message.reply("✅ Reaksiyalar saqlandi. /reactall deb yozing.")

@app.on_message(filters.private & filters.command("reactall"))
def react_all(client, message):
    uid = str(message.from_user.id)
    today = str(date.today())
    data = load_data()

    if today not in data["admins"] or uid not in data["admins"][today]:
        message.reply("❗ Avval /setreactions qiling")
        return

    emojis = data["admins"][today][uid]
    posts = data["posts"].get(today, [])

    if not posts:
        message.reply("Bugun kanalga post yo‘q")
        return

    for msg_id in posts:
        for emoji in emojis:
            try:
                client.set_reaction(
                    chat_id=CHANNEL_ID,
                    message_id=msg_id,
                    reaction=[ReactionTypeEmoji(emoji=emoji)]
                )
            except:
                pass

    message.reply(f"✅ {len(posts)} ta postga reaksiyalar qo‘yildi")

app.run()
