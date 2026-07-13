import asyncio
import json
import os
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
import aiohttp

# --- Configuration ---
api_id = os.getenv('ENDFLO_TELEGRAM_ID')
api_hash = os.getenv('ENDFLO_TELEGRAM_HASH')

N8N_WEBHOOK_URL = 'https://weironglee.tail40ab19.ts.net/webhook/f9aa4895-0173-426d-a399-3a36c1017ab2'
N8N_GROUP_EVENTS_WEBHOOK_URL = 'https://weironglee.tail40ab19.ts.net/webhook/47f4cf80-8a17-415d-a469-e731c317d96e'

# Directory to save media files (must match volume mount in n8n compose.yaml)
MEDIA_DIR = '/home/weirong/Documents/endflo/media'

client = TelegramClient('endflo_session', api_id, api_hash, flood_sleep_threshold=0)
me_id = None  # set in main() after client.start()


# --- Helpers ---

def get_content_type(message):
    """Determine content_type from Telethon message media attributes."""
    if not message.media:
        return 'text'
    if message.photo:
        return 'image'
    if message.video:
        return 'video'
    if message.voice or message.video_note:
        return 'voice' if message.voice else 'video_note'
    if message.sticker:
        return 'sticker'
    if message.animation:
        return 'gif'
    if message.document:
        return 'document'
    if message.audio:
        return 'audio'
    return 'unknown'


async def resolve_chat_name(client, event):
    """Resolve human-readable chat name."""
    try:
        chat = await event.get_chat()
        # Groups and channels have a title
        if hasattr(chat, 'title') and chat.title:
            return chat.title
        # DMs: use the other person's name
        if hasattr(chat, 'first_name'):
            parts = [chat.first_name or '', chat.last_name or '']
            return ' '.join(p for p in parts if p).strip() or str(event.chat_id)
    except Exception as e:
        print(f"Warning: Could not resolve chat name: {e}")
    return str(event.chat_id)


async def resolve_sender(client, message):
    """Resolve sender name and phone number from entity."""
    sender_name = str(message.sender_id)
    sender_phone = None
    try:
        sender = await message.get_sender()
        if sender:
            if hasattr(sender, 'first_name'):
                parts = [sender.first_name or '', sender.last_name or '']
                name = ' '.join(p for p in parts if p).strip()
                if name:
                    sender_name = name
                elif hasattr(sender, 'username') and sender.username:
                    sender_name = f"@{sender.username}"
            # Phone number (only available if user allows it in privacy settings)
            if hasattr(sender, 'phone') and sender.phone:
                sender_phone = f"+{sender.phone}"
    except Exception as e:
        print(f"Warning: Could not resolve sender: {e}")
    return sender_name, sender_phone


async def resolve_user_info(client, user_id):
    """Resolve a single user's name and phone from their ID. Returns {user_id, name, phone}."""
    try:
        entity = await client.get_entity(user_id)
        name = str(user_id)
        phone = None
        if entity:
            if hasattr(entity, 'first_name'):
                parts = [entity.first_name or '', entity.last_name or '']
                resolved = ' '.join(p for p in parts if p).strip()
                if resolved:
                    name = resolved
                elif hasattr(entity, 'username') and entity.username:
                    name = f"@{entity.username}"
            if hasattr(entity, 'phone') and entity.phone:
                phone = f"+{entity.phone}"
        return {"user_id": str(user_id), "name": name, "phone": phone}
    except Exception as e:
        print(f"Warning: Could not resolve user {user_id}: {e}")
        return {"user_id": str(user_id), "name": str(user_id), "phone": None}


def get_file_extension(message):
    """Get file extension based on media type."""
    if message.photo:
        return '.jpg'
    if message.video:
        return '.mp4'
    if message.voice:
        return '.ogg'
    if message.video_note:
        return '.mp4'
    if message.sticker:
        if message.sticker.is_animated:
            return '.tgs'
        if message.sticker.is_video:
            return '.webm'
        return '.webp'
    if message.animation:
        return '.gif'
    if message.document:
        name = getattr(message.file, 'name', None)
        if name:
            _, ext = os.path.splitext(name)
            return ext
    if message.audio:
        return '.mp3'
    return '.file'


async def save_media(message, msg_id):
    """Download media to disk and return the local file path."""
    os.makedirs(MEDIA_DIR, exist_ok=True)

    ext = get_file_extension(message)
    file_name = f"{msg_id}{ext}"
    file_path = os.path.join(MEDIA_DIR, file_name)

    try:
        await message.download_media(file=file_path)
        return file_path
    except Exception as e:
        print(f"Warning: Could not download media: {e}")
        return None


# --- 1. Read Past Messages ---
async def fetch_past_messages(channel_target, limit=10):
    print(f"\n--- Fetching past messages from {channel_target} ---")
    try:
        async for message in client.iter_messages(channel_target, limit=limit):
            chat_name = await resolve_chat_name(client, message)
            sender_name, sender_phone = await resolve_sender(client, message)
            content_type = get_content_type(message)

            print(f"[{message.date}] ID: {message.id} | Chat: {chat_name} | Sender: {sender_name} ({sender_phone or 'no phone'}) | Type: {content_type} | Text: {message.text}")

            await asyncio.sleep(2)

    except FloodWaitError as e:
        print(f"\nFloodWaitError triggered! Telegram requires a wait of {e.seconds} seconds.")
        print(f"Sleeping for {e.seconds}s...")
        await asyncio.sleep(e.seconds)
        print("Waking up! Resuming operations.")


# --- 2. Read Messages in Real-time ---
@client.on(events.NewMessage())
async def real_time_listener(event):
    message = event.message

    # Resolve names (requires entity lookups)
    chat_name = await resolve_chat_name(client, event)
    sender_name, sender_phone = await resolve_sender(client, message)
    content_type = get_content_type(message)

    # Save media to disk if present
    media_path = None
    media_file_name = None
    if message.media:
        media_path = await save_media(message, message.id)
        if media_path:
            media_file_name = os.path.basename(media_path)

    # Build unified payload
    payload = {
        "platform":        "telegram",
        "platform_msg_id": f"{event.chat_id}_{message.id}",
        "chat_id":         str(event.chat_id),
        "chat_name":       chat_name,
        "sender_id":       str(message.sender_id),
        "sender_name":     sender_name,
        "sender_phone":    sender_phone,
        "content":         message.message or "",
        "content_type":    content_type,
        "media_file_name": media_file_name,
        "media_path":      media_path,
        "quoted_message_id": f"{event.chat_id}_{message.reply_to.reply_to_msg_id}" if message.reply_to else None,
        "message_json":    message.to_dict(),
        "sent_at":         message.date.isoformat() if message.date else None,
    }

    # Send to n8n as plain JSON (no file attachment)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                N8N_WEBHOOK_URL,
                data=json.dumps(payload, default=str),
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    print(f"Sent to n8n | {chat_name} | {sender_name} | {content_type}")
                else:
                    print(f"n8n returned {response.status}")

    except Exception as e:
        print(f"Webhook request failed: {e}")


# --- 3. Group Lifecycle Events ---
@client.on(events.ChatAction())
async def group_event_listener(event):
    """Track group lifecycle: user added, name changes, participant changes."""
    event_type = None
    event_data = {}
    users_to_resolve = []  # collect user IDs to resolve in parallel

    if event.user_added:
        added_users = getattr(event, 'users', []) or [event.user_id]
        if me_id and me_id in added_users:
            event_type = "added_to_group"
            # Resolve the inviter (who added us)
            users_to_resolve.append(event.user_id)
        else:
            event_type = "participant_added"
            users_to_resolve.extend(added_users)

    elif event.user_kicked:
        event_type = "participant_removed"
        removed_users = getattr(event, 'users', []) or [event.user_id]
        users_to_resolve.extend(removed_users)
        if hasattr(event, 'removed_by') and event.removed_by:
            event_data["removed_by"] = str(event.removed_by)

    elif event.user_left:
        event_type = "participant_left"
        users_to_resolve.append(event.user_id)

    elif event.new_title:
        event_type = "group_name_changed"
        event_data["new_title"] = event.new_title

    # Skip uninteresting actions (pins, photo changes, etc.)
    if not event_type:
        return

    chat_name = await resolve_chat_name(client, event)

    # Resolve all involved users in parallel for name + phone
    resolved = {}
    if users_to_resolve:
        results = await asyncio.gather(
            *(resolve_user_info(client, uid) for uid in users_to_resolve),
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, dict):
                resolved[r["user_id"]] = r

    # Attach resolved user info to the payload
    if event_type == "added_to_group":
        event_data["invited_by"] = resolved.get(str(event.user_id), {"user_id": str(event.user_id), "name": str(event.user_id), "phone": None})
    elif event_type == "participant_added":
        event_data["added_users"] = [resolved.get(str(u), {"user_id": str(u), "name": str(u), "phone": None}) for u in added_users]
    elif event_type == "participant_removed":
        event_data["removed_users"] = [resolved.get(str(u), {"user_id": str(u), "name": str(u), "phone": None}) for u in removed_users]
    elif event_type == "participant_left":
        event_data["left_user"] = resolved.get(str(event.user_id), {"user_id": str(event.user_id), "name": str(event.user_id), "phone": None})

    payload = {
        "platform":         "telegram",
        "event_type":       event_type,
        "chat_id":          str(event.chat_id),
        "chat_name":        chat_name,
        "timestamp":        event.action_message.date.isoformat() if event.action_message and event.action_message.date else None,
    }
    payload.update(event_data)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                N8N_GROUP_EVENTS_WEBHOOK_URL,
                data=json.dumps(payload, default=str),
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    print(f"Group event → n8n | {event_type} | {chat_name}")
                else:
                    print(f"Group event n8n returned {response.status}")
    except Exception as e:
        print(f"Group event webhook failed: {e}")


# --- Main Execution ---
async def main():
    global me_id
    await client.start()
    me = await client.get_me()
    me_id = me.id
    print(f"Client successfully connected! (user_id={me_id})")

    # Uncomment to fetch past messages:
    # await fetch_past_messages('target_chat_or_channel', limit=10)

    print(f"\nListening for new messages... (Press Ctrl+C to stop)")
    await client.run_until_disconnected()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
