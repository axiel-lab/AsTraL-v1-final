import aiosqlite
from config import DB_PATH

_db = None

async def init():
    global _db
    _db = await aiosqlite.connect(DB_PATH)
    
    tables = [
        "CREATE TABLE IF NOT EXISTS custom_commands (guild_id TEXT, name TEXT, response TEXT, created_by TEXT, PRIMARY KEY (guild_id, name))",
        "CREATE TABLE IF NOT EXISTS ticket_config (guild_id TEXT PRIMARY KEY, category_id TEXT, staff_role_id TEXT, log_channel_id TEXT)",
        "CREATE TABLE IF NOT EXISTS tickets (channel_id TEXT PRIMARY KEY, guild_id TEXT, user_id TEXT)",
        "CREATE TABLE IF NOT EXISTS nickname_config (guild_id TEXT PRIMARY KEY, channel_id TEXT, note_text TEXT)",
        "CREATE TABLE IF NOT EXISTS sticky_messages (channel_id TEXT PRIMARY KEY, message_id TEXT, content TEXT)",
        "CREATE TABLE IF NOT EXISTS welcome_config (guild_id TEXT PRIMARY KEY, channel_id TEXT, message TEXT, role_id TEXT)",
        "CREATE TABLE IF NOT EXISTS giveaways (message_id TEXT PRIMARY KEY, channel_id TEXT, prize TEXT, end_time INTEGER, host_id TEXT, winners INTEGER)",
        "CREATE TABLE IF NOT EXISTS levels (guild_id TEXT, user_id TEXT, xp INTEGER DEFAULT 0, level INTEGER DEFAULT 0, last_msg INTEGER DEFAULT 0, PRIMARY KEY (guild_id, user_id))",
        "CREATE TABLE IF NOT EXISTS button_roles (message_id TEXT, role_id TEXT, emoji TEXT, label TEXT, PRIMARY KEY (message_id, role_id))",
        "CREATE TABLE IF NOT EXISTS automod_config (guild_id TEXT PRIMARY KEY, log_channel TEXT, anti_invite INTEGER, anti_spam INTEGER, anti_caps INTEGER, anti_links INTEGER)",
        "CREATE TABLE IF NOT EXISTS logging_config (guild_id TEXT PRIMARY KEY, msg_log TEXT, member_log TEXT)",
        "CREATE TABLE IF NOT EXISTS afk (guild_id TEXT, user_id TEXT, reason TEXT, PRIMARY KEY (guild_id, user_id))",
        "CREATE TABLE IF NOT EXISTS temp_voice_hub (guild_id TEXT PRIMARY KEY, channel_id TEXT)",
        "CREATE TABLE IF NOT EXISTS temp_voice_channels (channel_id TEXT PRIMARY KEY, owner_id TEXT)",
        "CREATE TABLE IF NOT EXISTS trusted_users (channel_id TEXT, user_id TEXT, PRIMARY KEY (channel_id, user_id))",
        "CREATE TABLE IF NOT EXISTS blocked_users (channel_id TEXT, user_id TEXT, PRIMARY KEY (channel_id, user_id))",
        "CREATE TABLE IF NOT EXISTS starboard (guild_id TEXT PRIMARY KEY, channel_id TEXT)",
        "CREATE TABLE IF NOT EXISTS starboard_msgs (original_id TEXT PRIMARY KEY, star_id TEXT)",
        "CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, channel_id TEXT, end_time INTEGER, text TEXT)",
        "CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id TEXT, author TEXT, content TEXT)",
        "CREATE TABLE IF NOT EXISTS stats (guild_id TEXT, channel_id TEXT, type TEXT)",
        "CREATE TABLE IF NOT EXISTS bump (guild_id TEXT PRIMARY KEY, end_time INTEGER)",
        "CREATE TABLE IF NOT EXISTS counting (guild_id TEXT PRIMARY KEY, channel_id TEXT, current_count INTEGER DEFAULT 0, last_user TEXT)",
        "CREATE TABLE IF NOT EXISTS mention_responders (guild_id TEXT, target_id TEXT, response TEXT, PRIMARY KEY (guild_id, target_id))",
        "CREATE TABLE IF NOT EXISTS warnings (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id TEXT, user_id TEXT, mod_id TEXT, reason TEXT)",
        "CREATE TABLE IF NOT EXISTS temp_roles (guild_id TEXT, user_id TEXT, role_id TEXT, end_time INTEGER)",
        "CREATE TABLE IF NOT EXISTS suggestions (message_id TEXT PRIMARY KEY, channel_id TEXT, author_id TEXT, text TEXT)",
        "CREATE TABLE IF NOT EXISTS highlights (guild_id TEXT, user_id TEXT, keyword TEXT, PRIMARY KEY (guild_id, user_id, keyword))",
        "CREATE TABLE IF NOT EXISTS staff_notes (id INTEGER PRIMARY KEY AUTOINCREMENT, guild_id TEXT, user_id TEXT, author_id TEXT, note TEXT)"
    ]
    for t in tables:
        await _db.execute(t)
    await _db.commit()

# --- Custom Commands ---
async def save(gid, name, response, uid):
    await _db.execute("INSERT OR REPLACE INTO custom_commands VALUES (?, ?, ?, ?)", (str(gid), name, response, str(uid)))
    await _db.commit()
async def get(gid, name):
    async with _db.execute("SELECT response FROM custom_commands WHERE guild_id = ? AND name = ?", (str(gid), name)) as c:
        r = await c.fetchone(); return r[0] if r else None
async def delete(gid, name):
    await _db.execute("DELETE FROM custom_commands WHERE guild_id = ? AND name = ?", (str(gid), name))
    await _db.commit()
async def list_all(gid):
    async with _db.execute("SELECT name, response FROM custom_commands WHERE guild_id = ? ORDER BY name", (str(gid),)) as c:
        return await c.fetchall()

# --- Tickets ---
async def set_ticket_config(gid, cat, role, log):
    await _db.execute("INSERT OR REPLACE INTO ticket_config VALUES (?, ?, ?, ?)", (str(gid), str(cat), str(role), str(log)))
    await _db.commit()
async def get_ticket_config(gid):
    async with _db.execute("SELECT category_id, staff_role_id, log_channel_id FROM ticket_config WHERE guild_id = ?", (str(gid),)) as c:
        return await c.fetchone()
async def add_ticket(cid, gid, uid):
    await _db.execute("INSERT INTO tickets VALUES (?, ?, ?)", (str(cid), str(gid), str(uid)))
    await _db.commit()
async def get_user_ticket(gid, uid):
    async with _db.execute("SELECT channel_id FROM tickets WHERE guild_id = ? AND user_id = ?", (str(gid), str(uid))) as c:
        r = await c.fetchone(); return r[0] if r else None
async def remove_ticket(cid):
    await _db.execute("DELETE FROM tickets WHERE channel_id = ?", (str(cid),))
    await _db.commit()

# --- Nicknames ---
async def set_nickname_channel(gid, cid, note):
    await _db.execute("INSERT OR REPLACE INTO nickname_config VALUES (?, ?, ?)", (str(gid), str(cid), note))
    await _db.commit()
async def get_nickname_config(gid):
    async with _db.execute("SELECT channel_id, note_text FROM nickname_config WHERE guild_id = ?", (str(gid),)) as c:
        return await c.fetchone()
async def set_sticky(cid, mid, text):
    await _db.execute("INSERT OR REPLACE INTO sticky_messages VALUES (?, ?, ?)", (str(cid), str(mid), text))
    await _db.commit()
async def get_sticky(cid):
    async with _db.execute("SELECT message_id, content FROM sticky_messages WHERE channel_id = ?", (str(cid),)) as c:
        return await c.fetchone()

# --- Welcome ---
async def set_welcome(gid, cid, msg, rid):
    await _db.execute("INSERT OR REPLACE INTO welcome_config VALUES (?, ?, ?, ?)", (str(gid), str(cid), msg, str(rid) if rid else None))
    await _db.commit()
async def get_welcome(gid):
    async with _db.execute("SELECT channel_id, message, role_id FROM welcome_config WHERE guild_id = ?", (str(gid),)) as c:
        return await c.fetchone()

# --- Giveaways ---
async def add_giveaway(mid, cid, prize, end, host, winners):
    await _db.execute("INSERT INTO giveaways VALUES (?, ?, ?, ?, ?, ?)", (str(mid), str(cid), prize, end, str(host), winners))
    await _db.commit()
async def get_giveaways():
    async with _db.execute("SELECT message_id, channel_id, prize, end_time, host_id, winners FROM giveaways") as c:
        return await c.fetchall()
async def remove_giveaway(mid):
    await _db.execute("DELETE FROM giveaways WHERE message_id = ?", (str(mid),))
    await _db.commit()

# --- Levels ---
async def get_level_data(gid, uid):
    async with _db.execute("SELECT xp, level, last_msg FROM levels WHERE guild_id = ? AND user_id = ?", (str(gid), str(uid))) as c:
        r = await c.fetchone(); return r if r else (0, 0, 0)
async def update_level_data(gid, uid, xp, lvl, last):
    await _db.execute("INSERT INTO levels (guild_id, user_id, xp, level, last_msg) VALUES (?, ?, ?, ?, ?) ON CONFLICT(guild_id, user_id) DO UPDATE SET xp=?, level=?, last_msg=?", (str(gid), str(uid), xp, lvl, last, xp, lvl, last))
    await _db.commit()
async def get_top_levels(gid):
    async with _db.execute("SELECT user_id, xp, level FROM levels WHERE guild_id = ? ORDER BY xp DESC LIMIT 10", (str(gid),)) as c:
        return await c.fetchall()

# --- Button Roles ---
async def add_button_role(mid, rid, emoji, label):
    await _db.execute("INSERT OR REPLACE INTO button_roles VALUES (?, ?, ?, ?)", (str(mid), str(rid), emoji, label))
    await _db.commit()
async def get_all_button_roles():
    async with _db.execute("SELECT message_id, role_id, emoji, label FROM button_roles") as c:
        return await c.fetchall()
async def get_button_roles_for_message(mid):
    async with _db.execute("SELECT message_id, role_id, emoji, label FROM button_roles WHERE message_id = ?", (str(mid),)) as c:
        return await c.fetchall()

# --- AutoMod ---
async def set_automod(gid, log, inv, spam, caps, links):
    await _db.execute("INSERT OR REPLACE INTO automod_config VALUES (?, ?, ?, ?, ?, ?)", (str(gid), str(log) if log else None, inv, spam, caps, links))
    await _db.commit()
async def get_automod(gid):
    async with _db.execute("SELECT log_channel, anti_invite, anti_spam, anti_caps, anti_links FROM automod_config WHERE guild_id = ?", (str(gid),)) as c:
        return await c.fetchone()

# --- Logging ---
async def set_logging(gid, msg, mem):
    await _db.execute("INSERT OR REPLACE INTO logging_config VALUES (?, ?, ?)", (str(gid), str(msg) if msg else None, str(mem) if mem else None))
    await _db.commit()
async def get_logging(gid):
    async with _db.execute("SELECT msg_log, member_log FROM logging_config WHERE guild_id = ?", (str(gid),)) as c:
        return await c.fetchone()

# --- AFK ---
async def set_afk(gid, uid, reason):
    await _db.execute("INSERT OR REPLACE INTO afk VALUES (?, ?, ?)", (str(gid), str(uid), reason))
    await _db.commit()
async def get_afk(gid, uid):
    async with _db.execute("SELECT reason FROM afk WHERE guild_id = ? AND user_id = ?", (str(gid), str(uid))) as c:
        r = await c.fetchone(); return r[0] if r else None
async def remove_afk(gid, uid):
    await _db.execute("DELETE FROM afk WHERE guild_id = ? AND user_id = ?", (str(gid), str(uid)))
    await _db.commit()

# --- Temp Voice ---
async def set_temp_hub(gid, cid):
    await _db.execute("INSERT OR REPLACE INTO temp_voice_hub VALUES (?, ?)", (str(gid), str(cid)))
    await _db.commit()
async def get_temp_hub(gid):
    async with _db.execute("SELECT channel_id FROM temp_voice_hub WHERE guild_id = ?", (str(gid),)) as c:
        r = await c.fetchone(); return r[0] if r else None
async def add_temp_channel(cid, uid):
    await _db.execute("INSERT INTO temp_voice_channels VALUES (?, ?)", (str(cid), str(uid)))
    await _db.commit()
async def get_temp_channel(cid):
    async with _db.execute("SELECT owner_id FROM temp_voice_channels WHERE channel_id = ?", (str(cid),)) as c:
        r = await c.fetchone(); return r[0] if r else None
async def remove_temp_channel(cid):
    await _db.execute("DELETE FROM temp_voice_channels WHERE channel_id = ?", (str(cid),))
    await _db.commit()
async def add_trusted(cid, uid):
    await _db.execute("INSERT OR IGNORE INTO trusted_users VALUES (?, ?)", (str(cid), str(uid)))
    await _db.commit()
async def add_blocked(cid, uid):
    await _db.execute("INSERT OR IGNORE INTO blocked_users VALUES (?, ?)", (str(cid), str(uid)))
    await _db.commit()
async def update_temp_owner(cid, new_owner):
    await _db.execute("UPDATE temp_voice_channels SET owner_id = ? WHERE channel_id = ?", (str(new_owner), str(cid)))
    await _db.commit()
async def clean_vc(cid):
    await _db.execute("DELETE FROM trusted_users WHERE channel_id = ?", (str(cid),))
    await _db.execute("DELETE FROM blocked_users WHERE channel_id = ?", (str(cid),))
    await _db.execute("DELETE FROM temp_voice_channels WHERE channel_id = ?", (str(cid),))
    await _db.commit()

# --- Starboard ---
async def set_starboard(gid, cid):
    await _db.execute("INSERT OR REPLACE INTO starboard VALUES (?, ?)", (str(gid), str(cid)))
    await _db.commit()
async def get_starboard(gid):
    async with _db.execute("SELECT channel_id FROM starboard WHERE guild_id = ?", (str(gid),)) as c:
        r = await c.fetchone(); return r[0] if r else None
async def add_star(mid, sid):
    await _db.execute("INSERT OR REPLACE INTO starboard_msgs VALUES (?, ?)", (str(mid), str(sid)))
    await _db.commit()
async def get_star(mid):
    async with _db.execute("SELECT star_id FROM starboard_msgs WHERE original_id = ?", (str(mid),)) as c:
        r = await c.fetchone(); return r[0] if r else None

# --- Reminders ---
async def add_reminder(uid, cid, time, text):
    await _db.execute("INSERT INTO reminders (user_id, channel_id, end_time, text) VALUES (?, ?, ?, ?)", (str(uid), str(cid), time, text))
    await _db.commit()
async def get_reminders():
    async with _db.execute("SELECT id, user_id, channel_id, text FROM reminders WHERE end_time <= strftime('%s', 'now')") as c:
        return await c.fetchall()
async def remove_reminder(rid):
    await _db.execute("DELETE FROM reminders WHERE id = ?", (rid,))
    await _db.commit()

# --- Quotes ---
async def add_quote(gid, author, content):
    await _db.execute("INSERT INTO quotes (guild_id, author, content) VALUES (?, ?, ?)", (str(gid), author, content))
    await _db.commit()
async def get_quote(gid):
    async with _db.execute("SELECT author, content FROM quotes WHERE guild_id = ? ORDER BY RANDOM() LIMIT 1", (str(gid),)) as c:
        return await c.fetchone()

# --- Stats ---
async def set_stat(gid, cid, type):
    await _db.execute("INSERT INTO stats VALUES (?, ?, ?)", (str(gid), str(cid), type))
    await _db.commit()
async def get_stats():
    async with _db.execute("SELECT guild_id, channel_id, type FROM stats") as c:
        return await c.fetchall()

# --- Bump ---
async def set_bump(gid, time):
    await _db.execute("INSERT OR REPLACE INTO bump VALUES (?, ?)", (str(gid), time))
    await _db.commit()
async def get_bump(gid):
    async with _db.execute("SELECT end_time FROM bump WHERE guild_id = ?", (str(gid),)) as c:
        r = await c.fetchone(); return r[0] if r else 0

# --- Counting ---
async def set_counting_channel(gid, cid):
    await _db.execute("INSERT OR REPLACE INTO counting VALUES (?, ?, 0, NULL)", (str(gid), str(cid)))
    await _db.commit()
async def get_counting(gid):
    async with _db.execute("SELECT channel_id, current_count, last_user FROM counting WHERE guild_id = ?", (str(gid),)) as c:
        return await c.fetchone()
async def update_counting(gid, count, uid):
    await _db.execute("UPDATE counting SET current_count = ?, last_user = ? WHERE guild_id = ?", (count, str(uid), str(gid)))
    await _db.commit()

# --- Mention Responders ---
async def set_mention_responder(gid, target_id, response):
    await _db.execute("INSERT OR REPLACE INTO mention_responders VALUES (?, ?, ?)", (str(gid), str(target_id), response))
    await _db.commit()
async def get_mention_responders(gid):
    async with _db.execute("SELECT target_id, response FROM mention_responders WHERE guild_id = ?", (str(gid),)) as c:
        return await c.fetchall()
async def remove_mention_responder(gid, target_id):
    await _db.execute("DELETE FROM mention_responders WHERE guild_id = ? AND target_id = ?", (str(gid), str(target_id)))
    await _db.commit()

# --- Warnings ---
async def add_warning(gid, uid, mid, reason):
    await _db.execute("INSERT INTO warnings (guild_id, user_id, mod_id, reason) VALUES (?, ?, ?, ?)", (str(gid), str(uid), str(mid), reason))
    await _db.commit()
async def get_warnings(gid, uid):
    async with _db.execute("SELECT id, mod_id, reason FROM warnings WHERE guild_id = ? AND user_id = ?", (str(gid), str(uid))) as c:
        return await c.fetchall()
async def clear_warnings(gid, uid):
    await _db.execute("DELETE FROM warnings WHERE guild_id = ? AND user_id = ?", (str(gid), str(uid)))
    await _db.commit()

# --- Temp Roles ---
async def add_temp_role(gid, uid, rid, end):
    await _db.execute("INSERT INTO temp_roles VALUES (?, ?, ?, ?)", (str(gid), str(uid), str(rid), end))
    await _db.commit()
async def get_expired_roles():
    async with _db.execute("SELECT guild_id, user_id, role_id FROM temp_roles WHERE end_time <= strftime('%s', 'now')") as c:
        return await c.fetchall()
async def remove_temp_role(gid, uid, rid):
    await _db.execute("DELETE FROM temp_roles WHERE guild_id = ? AND user_id = ? AND role_id = ?", (str(gid), str(uid), str(rid)))
    await _db.commit()

# --- Suggestions ---
async def add_suggestion(mid, cid, uid, text):
    await _db.execute("INSERT INTO suggestions VALUES (?, ?, ?, ?)", (str(mid), str(cid), str(uid), text))
    await _db.commit()

# --- Highlights ---
async def add_highlight(gid, uid, keyword):
    await _db.execute("INSERT OR IGNORE INTO highlights VALUES (?, ?, ?)", (str(gid), str(uid), keyword.lower()))
    await _db.commit()
async def remove_highlight(gid, uid, keyword):
    await _db.execute("DELETE FROM highlights WHERE guild_id = ? AND user_id = ? AND keyword = ?", (str(gid), str(uid), keyword.lower()))
    await _db.commit()
async def get_user_highlights(gid, uid):
    async with _db.execute("SELECT keyword FROM highlights WHERE guild_id = ? AND user_id = ?", (str(gid), str(uid))) as c:
        return await c.fetchall()
async def get_all_highlights(gid):
    async with _db.execute("SELECT user_id, keyword FROM highlights WHERE guild_id = ?", (str(gid),)) as c:
        return await c.fetchall()

# --- Staff Notes ---
async def add_note(gid, uid, author_id, note):
    await _db.execute("INSERT INTO staff_notes (guild_id, user_id, author_id, note) VALUES (?, ?, ?, ?)", (str(gid), str(uid), str(author_id), note))
    await _db.commit()
async def get_notes(gid, uid):
    async with _db.execute("SELECT id, author_id, note FROM staff_notes WHERE guild_id = ? AND user_id = ?", (str(gid), str(uid))) as c:
        return await c.fetchall()
async def delete_note(nid):
    await _db.execute("DELETE FROM staff_notes WHERE id = ?", (nid,))
    await _db.commit()