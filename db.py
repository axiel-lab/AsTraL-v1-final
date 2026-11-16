import os
from motor.motor_asyncio import AsyncIOMotorClient

client = None
db = None

async def init():
    global client, db
    uri = os.getenv("MONGO_URI")
    if not uri: return
    
    client = AsyncIOMotorClient(uri)
    db = client.astral_bot
    
    await db.custom_commands.create_index([("guild_id", 1), ("name", 1)], unique=True)
    await db.levels.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
    await db.warnings.create_index([("guild_id", 1), ("user_id", 1)])
    await db.button_roles.create_index([("message_id", 1), ("role_id", 1)], unique=True)
    await db.afk.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
    await db.highlights.create_index([("guild_id", 1), ("user_id", 1), ("keyword", 1)], unique=True)
    await db.tickets.create_index([("channel_id", 1)], unique=True)
    await db.giveaways.create_index([("message_id", 1)], unique=True)
    await db.marriages.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
    await db.birthdays.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
    await db.sticky_roles.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
    await db.autoresponders.create_index([("guild_id", 1), ("trigger", 1)], unique=True)
    await db.honeypot_config.create_index([("guild_id", 1)], unique=True)

# Commands
async def save(gid, name, response, uid):
    await db.custom_commands.update_one({"guild_id": str(gid), "name": name}, {"$set": {"response": response, "created_by": str(uid)}}, upsert=True)
async def get(gid, name):
    doc = await db.custom_commands.find_one({"guild_id": str(gid), "name": name})
    return doc["response"] if doc else None
async def delete(gid, name):
    await db.custom_commands.delete_one({"guild_id": str(gid), "name": name})
async def list_all(gid):
    cursor = db.custom_commands.find({"guild_id": str(gid)}).sort("name", 1)
    return [(doc["name"], doc["response"]) async for doc in cursor]

# Tickets
async def set_ticket_config(gid, cat, role, log):
    await db.ticket_config.update_one({"guild_id": str(gid)}, {"$set": {"category_id": str(cat), "staff_role_id": str(role), "log_channel_id": str(log)}}, upsert=True)
async def get_ticket_config(gid):
    doc = await db.ticket_config.find_one({"guild_id": str(gid)})
    if doc: return (doc["category_id"], doc["staff_role_id"], doc["log_channel_id"])
    return None
async def add_ticket(cid, gid, uid):
    await db.tickets.update_one({"channel_id": str(cid)}, {"$set": {"guild_id": str(gid), "user_id": str(uid)}}, upsert=True)
async def get_user_ticket(gid, uid):
    doc = await db.tickets.find_one({"guild_id": str(gid), "user_id": str(uid)})
    return doc["channel_id"] if doc else None
async def remove_ticket(cid):
    await db.tickets.delete_one({"channel_id": str(cid)})

# Nicknames
async def set_nickname_channel(gid, cid, note):
    await db.nickname_config.update_one({"guild_id": str(gid)}, {"$set": {"channel_id": str(cid), "note_text": note}}, upsert=True)
async def get_nickname_config(gid):
    doc = await db.nickname_config.find_one({"guild_id": str(gid)})
    if doc: return (doc["channel_id"], doc["note_text"])
    return None
async def set_sticky(cid, mid, text):
    await db.sticky_messages.update_one({"channel_id": str(cid)}, {"$set": {"message_id": str(mid), "content": text}}, upsert=True)
async def get_sticky(cid):
    doc = await db.sticky_messages.find_one({"channel_id": str(cid)})
    if doc: return (doc["message_id"], doc["content"])
    return None

# Welcome
async def set_welcome(gid, cid, msg, rid):
    await db.welcome_config.update_one({"guild_id": str(gid)}, {"$set": {"channel_id": str(cid), "message": msg, "role_id": str(rid) if rid else None}}, upsert=True)
async def get_welcome(gid):
    doc = await db.welcome_config.find_one({"guild_id": str(gid)})
    if doc: return (doc["channel_id"], doc["message"], doc.get("role_id"))
    return None

# Giveaways
async def add_giveaway(mid, cid, prize, end, host, winners):
    await db.giveaways.update_one({"message_id": str(mid)}, {"$set": {"channel_id": str(cid), "prize": prize, "end_time": end, "host_id": str(host), "winners": winners}}, upsert=True)
async def get_giveaways():
    cursor = db.giveaways.find({})
    return [(doc["message_id"], doc["channel_id"], doc["prize"], doc["end_time"], doc["host_id"], doc["winners"]) async for doc in cursor]
async def remove_giveaway(mid):
    await db.giveaways.delete_one({"message_id": str(mid)})

# Levels
async def get_level_data(gid, uid):
    doc = await db.levels.find_one({"guild_id": str(gid), "user_id": str(uid)})
    if doc: return (doc["xp"], doc["level"], doc["last_msg"])
    return (0, 0, 0)
async def update_level_data(gid, uid, xp, lvl, last):
    await db.levels.update_one({"guild_id": str(gid), "user_id": str(uid)}, {"$set": {"xp": xp, "level": lvl, "last_msg": last}}, upsert=True)
async def get_top_levels(gid):
    cursor = db.levels.find({"guild_id": str(gid)}).sort("xp", -1).limit(10)
    return [(doc["user_id"], doc["xp"], doc["level"]) async for doc in cursor]

# Economy
async def add_coins(gid, uid, amount):
    await db.economy.update_one({"guild_id": str(gid), "user_id": str(uid)}, {"$inc": {"balance": amount}}, upsert=True)
async def get_balance(gid, uid):
    doc = await db.economy.find_one({"guild_id": str(gid), "user_id": str(uid)})
    return doc["balance"] if doc else 0

# Button Roles
async def add_button_role(mid, rid, emoji, label):
    await db.button_roles.update_one({"message_id": str(mid), "role_id": str(rid)}, {"$set": {"emoji": emoji, "label": label}}, upsert=True)
async def get_all_button_roles():
    cursor = db.button_roles.find({})
    return [(doc["message_id"], doc["role_id"], doc["emoji"], doc["label"]) async for doc in cursor]
async def get_button_roles_for_message(mid):
    cursor = db.button_roles.find({"message_id": str(mid)})
    return [(doc["message_id"], doc["role_id"], doc["emoji"], doc["label"]) async for doc in cursor]

# AutoMod
async def set_automod(gid, log, inv, spam, caps, links):
    await db.automod_config.update_one({"guild_id": str(gid)}, {"$set": {"log_channel": str(log) if log else None, "anti_invite": inv, "anti_spam": spam, "anti_caps": caps, "anti_links": links}}, upsert=True)
async def get_automod(gid):
    doc = await db.automod_config.find_one({"guild_id": str(gid)})
    if doc: return (doc.get("log_channel"), doc["anti_invite"], doc["anti_spam"], doc["anti_caps"], doc["anti_links"])
    return None

# Logging
async def set_logging(gid, msg, mem):
    await db.logging_config.update_one({"guild_id": str(gid)}, {"$set": {"msg_log": str(msg) if msg else None, "member_log": str(mem) if mem else None}}, upsert=True)
async def get_logging(gid):
    doc = await db.logging_config.find_one({"guild_id": str(gid)})
    if doc: return (doc.get("msg_log"), doc.get("member_log"))
    return None

# AFK
async def set_afk(gid, uid, reason):
    await db.afk.update_one({"guild_id": str(gid), "user_id": str(uid)}, {"$set": {"reason": reason}}, upsert=True)
async def get_afk(gid, uid):
    doc = await db.afk.find_one({"guild_id": str(gid), "user_id": str(uid)})
    return doc["reason"] if doc else None
async def remove_afk(gid, uid):
    await db.afk.delete_one({"guild_id": str(gid), "user_id": str(uid)})

# Temp Voice
async def set_temp_hub(gid, cid):
    await db.temp_voice_hub.update_one({"guild_id": str(gid)}, {"$set": {"channel_id": str(cid)}}, upsert=True)
async def get_temp_hub(gid):
    doc = await db.temp_voice_hub.find_one({"guild_id": str(gid)})
    return doc["channel_id"] if doc else None
async def add_temp_channel(cid, uid):
    await db.temp_voice_channels.update_one({"channel_id": str(cid)}, {"$set": {"owner_id": str(uid)}}, upsert=True)
async def get_temp_channel(cid):
    doc = await db.temp_voice_channels.find_one({"channel_id": str(cid)})
    return doc["owner_id"] if doc else None
async def remove_temp_channel(cid):
    await db.temp_voice_channels.delete_one({"channel_id": str(cid)})
async def add_trusted(cid, uid):
    await db.temp_voice_channels.update_one({"channel_id": str(cid)}, {"$addToSet": {"trusted": str(uid)}})
async def add_blocked(cid, uid):
    await db.temp_voice_channels.update_one({"channel_id": str(cid)}, {"$addToSet": {"blocked": str(uid)}})
async def update_temp_owner(cid, new_owner):
    await db.temp_voice_channels.update_one({"channel_id": str(cid)}, {"$set": {"owner_id": str(new_owner)}})
async def clean_vc(cid):
    await db.temp_voice_channels.delete_one({"channel_id": str(cid)})

# Starboard
async def set_starboard(gid, cid):
    await db.starboard.update_one({"guild_id": str(gid)}, {"$set": {"channel_id": str(cid)}}, upsert=True)
async def get_starboard(gid):
    doc = await db.starboard.find_one({"guild_id": str(gid)})
    return doc["channel_id"] if doc else None
async def add_star(mid, sid):
    await db.starboard_msgs.update_one({"original_id": str(mid)}, {"$set": {"star_id": str(sid)}}, upsert=True)
async def get_star(mid):
    doc = await db.starboard_msgs.find_one({"original_id": str(mid)})
    return doc["star_id"] if doc else None

# Reminders
async def add_reminder(uid, cid, time, text):
    await db.reminders.insert_one({"user_id": str(uid), "channel_id": str(cid), "end_time": time, "text": text})
async def get_reminders():
    import time
    cursor = db.reminders.find({"end_time": {"$lte": int(time.time())}})
    return [(doc["_id"], doc["user_id"], doc["channel_id"], doc["text"]) async for doc in cursor]
async def remove_reminder(rid):
    from bson.objectid import ObjectId
    await db.reminders.delete_one({"_id": ObjectId(rid)})

# Quotes
async def add_quote(gid, author, content):
    await db.quotes.insert_one({"guild_id": str(gid), "author": author, "content": content})
async def get_quote(gid):
    pipeline = [{"$match": {"guild_id": str(gid)}}, {"$sample": {"size": 1}}]
    cursor = db.quotes.aggregate(pipeline)
    docs = [doc async for doc in cursor]
    if docs: return (docs[0]["author"], docs[0]["content"])
    return None

# Stats
async def set_stat(gid, cid, type):
    await db.stats.update_one({"guild_id": str(gid), "type": type}, {"$set": {"channel_id": str(cid)}}, upsert=True)
async def get_stats():
    cursor = db.stats.find({})
    return [(doc["guild_id"], doc["channel_id"], doc["type"]) async for doc in cursor]

# Bump
async def set_bump(gid, time):
    await db.bump.update_one({"guild_id": str(gid)}, {"$set": {"end_time": time}}, upsert=True)
async def get_bump(gid):
    doc = await db.bump.find_one({"guild_id": str(gid)})
    return doc["end_time"] if doc else 0

# Counting
async def set_counting_channel(gid, cid):
    await db.counting.update_one({"guild_id": str(gid)}, {"$set": {"channel_id": str(cid), "current_count": 0, "last_user": None}}, upsert=True)
async def get_counting(gid):
    doc = await db.counting.find_one({"guild_id": str(gid)})
    if doc: return (doc["channel_id"], doc["current_count"], doc.get("last_user"))
    return None
async def update_counting(gid, count, uid):
    await db.counting.update_one({"guild_id": str(gid)}, {"$set": {"current_count": count, "last_user": str(uid) if uid else None}})

# Mention Responders
async def set_mention_responder(gid, target_id, response):
    await db.mention_responders.update_one({"guild_id": str(gid), "target_id": str(target_id)}, {"$set": {"response": response}}, upsert=True)
async def get_mention_responders(gid):
    cursor = db.mention_responders.find({"guild_id": str(gid)})
    return [(doc["target_id"], doc["response"]) async for doc in cursor]
async def remove_mention_responder(gid, target_id):
    await db.mention_responders.delete_one({"guild_id": str(gid), "target_id": str(target_id)})

# Warnings
async def add_warning(gid, uid, mid, reason):
    await db.warnings.insert_one({"guild_id": str(gid), "user_id": str(uid), "mod_id": str(mid), "reason": reason})
async def get_warnings(gid, uid):
    cursor = db.warnings.find({"guild_id": str(gid), "user_id": str(uid)})
    return [(str(doc["_id"]), doc["mod_id"], doc["reason"]) async for doc in cursor]
async def clear_warnings(gid, uid):
    await db.warnings.delete_many({"guild_id": str(gid), "user_id": str(uid)})

# Temp Roles
async def add_temp_role(gid, uid, rid, end):
    await db.temp_roles.update_one({"guild_id": str(gid), "user_id": str(uid), "role_id": str(rid)}, {"$set": {"end_time": end}}, upsert=True)
async def get_expired_roles():
    import time
    cursor = db.temp_roles.find({"end_time": {"$lte": int(time.time())}})
    return [(doc["guild_id"], doc["user_id"], doc["role_id"]) async for doc in cursor]
async def remove_temp_role(gid, uid, rid):
    await db.temp_roles.delete_one({"guild_id": str(gid), "user_id": str(uid), "role_id": str(rid)})

# Suggestions
async def add_suggestion(mid, cid, uid, text):
    await db.suggestions.update_one({"message_id": str(mid)}, {"$set": {"channel_id": str(cid), "author_id": str(uid), "text": text}}, upsert=True)

# Highlights
async def add_highlight(gid, uid, keyword):
    await db.highlights.update_one({"guild_id": str(gid), "user_id": str(uid), "keyword": keyword.lower()}, {"$set": {"keyword": keyword.lower()}}, upsert=True)
async def remove_highlight(gid, uid, keyword):
    await db.highlights.delete_one({"guild_id": str(gid), "user_id": str(uid), "keyword": keyword.lower()})
async def get_user_highlights(gid, uid):
    cursor = db.highlights.find({"guild_id": str(gid), "user_id": str(uid)})
    return [(doc["keyword"],) async for doc in cursor]
async def get_all_highlights(gid):
    cursor = db.highlights.find({"guild_id": str(gid)})
    return [(doc["user_id"], doc["keyword"]) async for doc in cursor]

# Staff Notes
async def add_note(gid, uid, author_id, note):
    await db.staff_notes.insert_one({"guild_id": str(gid), "user_id": str(uid), "author_id": str(author_id), "note": note})
async def get_notes(gid, uid):
    cursor = db.staff_notes.find({"guild_id": str(gid), "user_id": str(uid)})
    return [(str(doc["_id"]), doc["author_id"], doc["note"]) async for doc in cursor]
async def delete_note(nid):
    from bson.objectid import ObjectId
    await db.staff_notes.delete_one({"_id": ObjectId(nid)})

# AI Channel
async def set_ai_channel(gid, cid):
    await db.ai_config.update_one({"guild_id": str(gid)}, {"$set": {"channel_id": str(cid)}}, upsert=True)
async def get_ai_channel(gid):
    doc = await db.ai_config.find_one({"guild_id": str(gid)})
    return doc["channel_id"] if doc else None

# Weather
async def set_weather_config(gid, cid, city):
    await db.weather_config.update_one({"guild_id": str(gid), "city": city.lower()}, {"$set": {"channel_id": str(cid), "city": city.lower()}}, upsert=True)
async def get_weather_configs():
    cursor = db.weather_config.find({})
    return [(doc["guild_id"], doc["channel_id"], doc["city"]) async for doc in cursor]
async def remove_weather_config(gid, city):
    await db.weather_config.delete_one({"guild_id": str(gid), "city": city.lower()})
async def remove_all_weather(gid):
    await db.weather_config.delete_many({"guild_id": str(gid)})

# Marriage
async def get_marriage(gid, uid):
    doc = await db.marriages.find_one({"guild_id": str(gid), "user_id": str(uid)})
    return doc["partner_id"] if doc else None
async def add_marriage(gid, uid1, uid2):
    await db.marriages.update_one({"guild_id": str(gid), "user_id": str(uid1)}, {"$set": {"partner_id": str(uid2)}}, upsert=True)
    await db.marriages.update_one({"guild_id": str(gid), "user_id": str(uid2)}, {"$set": {"partner_id": str(uid1)}}, upsert=True)
async def remove_marriage(gid, uid):
    partner = await get_marriage(gid, uid)
    await db.marriages.delete_one({"guild_id": str(gid), "user_id": str(uid)})
    if partner:
        await db.marriages.delete_one({"guild_id": str(gid), "user_id": str(partner)})

# Birthdays
async def set_birthday(gid, uid, month, day):
    await db.birthdays.update_one({"guild_id": str(gid), "user_id": str(uid)}, {"$set": {"month": month, "day": day}}, upsert=True)
async def get_todays_birthdays(gid, month, day):
    cursor = db.birthdays.find({"guild_id": str(gid), "month": month, "day": day})
    return [doc["user_id"] async for doc in cursor]
async def set_birthday_channel(gid, cid):
    await db.birthday_config.update_one({"guild_id": str(gid)}, {"$set": {"channel_id": str(cid)}}, upsert=True)
async def get_birthday_channel(gid):
    doc = await db.birthday_config.find_one({"guild_id": str(gid)})
    return doc["channel_id"] if doc else None

# Sticky Roles
async def save_sticky_roles(gid, uid, roles):
    await db.sticky_roles.update_one({"guild_id": str(gid), "user_id": str(uid)}, {"$set": {"roles": roles}}, upsert=True)
async def get_sticky_roles(gid, uid):
    doc = await db.sticky_roles.find_one({"guild_id": str(gid), "user_id": str(uid)})
    return doc["roles"] if doc else []

# Auto Responders
async def add_autoresponder(gid, trigger, response):
    await db.autoresponders.update_one({"guild_id": str(gid), "trigger": trigger.lower()}, {"$set": {"response": response}}, upsert=True)
async def get_autoresponders(gid):
    cursor = db.autoresponders.find({"guild_id": str(gid)})
    return [(doc["trigger"], doc["response"]) async for doc in cursor]
async def remove_autoresponder(gid, trigger):
    await db.autoresponders.delete_one({"guild_id": str(gid), "trigger": trigger.lower()})

# Honeypot
async def set_honeypot(gid, cid, mid):
    await db.honeypot_config.update_one({"guild_id": str(gid)}, {"$set": {"channel_id": str(cid), "message_id": str(mid), "bans": 0}}, upsert=True)
async def get_honeypot(gid):
    doc = await db.honeypot_config.find_one({"guild_id": str(gid)})
    return doc if doc else None
async def update_honeypot_bans(gid):
    await db.honeypot_config.update_one({"guild_id": str(gid)}, {"$inc": {"bans": 1}})
