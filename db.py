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
    
    # Existing Indexes
    await db.custom_commands.create_index([("guild_id", 1), ("name", 1)], unique=True)
    await db.levels.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
    await db.warnings.create_index([("guild_id", 1), ("user_id", 1)])
    await db.button_roles.create_index([("message_id", 1), ("role_id", 1)], unique=True)
    await db.afk.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
    await db.highlights.create_index([("guild_id", 1), ("user_id", 1), ("keyword", 1)], unique=True)
    await db.tickets.create_index([("channel_id", 1)], unique=True)
    await db.giveaways.create_index([("message_id", 1)], unique=True)
    await db.ai_config.create_index([("guild_id", 1)], unique=True)

    # New Indexes
    await db.marriages.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
    await db.birthdays.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
    await db.sticky_roles.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
    await db.autoresponders.create_index([("guild_id", 1), ("trigger", 1)], unique=True)
    await db.honeypot_config.create_index([("guild_id", 1)], unique=True)

# --- Levels & Economy ---
async def get_level_data(gid, uid):
    doc = await db.levels.find_one({"guild_id": str(gid), "user_id": str(uid)})
    if doc: return (doc["xp"], doc["level"], doc["last_msg"])
    return (0, 0, 0)
async def update_level_data(gid, uid, xp, lvl, last):
    await db.levels.update_one(
        {"guild_id": str(gid), "user_id": str(uid)},
        {"$set": {"xp": xp, "level": lvl, "last_msg": last}},
        upsert=True
    )
async def add_coins(gid, uid, amount):
    await db.economy.update_one(
        {"guild_id": str(gid), "user_id": str(uid)},
        {"$inc": {"balance": amount}},
        upsert=True
    )
async def get_balance(gid, uid):
    doc = await db.economy.find_one({"guild_id": str(gid), "user_id": str(uid)})
    return doc["balance"] if doc else 0

# --- Marriage ---
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

# --- Birthdays ---
async def set_birthday(gid, uid, month, day):
    await db.birthdays.update_one(
        {"guild_id": str(gid), "user_id": str(uid)},
        {"$set": {"month": month, "day": day}},
        upsert=True
    )
async def get_todays_birthdays(gid, month, day):
    cursor = db.birthdays.find({"guild_id": str(gid), "month": month, "day": day})
    return [doc["user_id"] async for doc in cursor]
async def set_birthday_channel(gid, cid):
    await db.birthday_config.update_one({"guild_id": str(gid)}, {"$set": {"channel_id": str(cid)}}, upsert=True)
async def get_birthday_channel(gid):
    doc = await db.birthday_config.find_one({"guild_id": str(gid)})
    return doc["channel_id"] if doc else None

# --- Sticky Roles ---
async def save_sticky_roles(gid, uid, roles):
    await db.sticky_roles.update_one(
        {"guild_id": str(gid), "user_id": str(uid)},
        {"$set": {"roles": roles}},
        upsert=True
    )
async def get_sticky_roles(gid, uid):
    doc = await db.sticky_roles.find_one({"guild_id": str(gid), "user_id": str(uid)})
    return doc["roles"] if doc else []

# --- Auto Responders ---
async def add_autoresponder(gid, trigger, response):
    await db.autoresponders.update_one(
        {"guild_id": str(gid), "trigger": trigger.lower()},
        {"$set": {"response": response}},
        upsert=True
    )
async def get_autoresponders(gid):
    cursor = db.autoresponders.find({"guild_id": str(gid)})
    return [(doc["trigger"], doc["response"]) async for doc in cursor]
async def remove_autoresponder(gid, trigger):
    await db.autoresponders.delete_one({"guild_id": str(gid), "trigger": trigger.lower()})

# --- Honeypot ---
async def set_honeypot(gid, cid, mid):
    await db.honeypot_config.update_one(
        {"guild_id": str(gid)},
        {"$set": {"channel_id": str(cid), "message_id": str(mid), "bans": 0}},
        upsert=True
    )
async def get_honeypot(gid):
    doc = await db.honeypot_config.find_one({"guild_id": str(gid)})
    return doc if doc else None
async def update_honeypot_bans(gid):
    await db.honeypot_config.update_one({"guild_id": str(gid)}, {"$inc": {"bans": 1}})
