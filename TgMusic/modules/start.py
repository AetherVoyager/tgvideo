#  Copyright (c) 2025 AshokShau
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the TgMusicBot project. All rights reserved where applicable.

from pytdbot import Client, types

from TgMusic import __version__
from TgMusic.core import (
    config,
    Filter,
    SupportButton,
)
from TgMusic.core.buttons import add_me_markup, HelpMenu, BackHelpMenu

startText = """
ʜᴇʏ {};

◎ ᴛʜɪꜱ ɪꜱ {}!
➻ ᴀ ꜰᴀꜱᴛ & ᴘᴏᴡᴇʀꜰᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜꜱɪᴄ & ᴠɪᴅᴇᴏ ᴘʟᴀʏᴇʀ ʙᴏᴛ ᴡɪᴛʜ ꜱᴏᴍᴇ ᴀᴡᴇꜱᴏᴍᴇ ꜰᴇᴀᴛᴜʀᴇꜱ.

ꜱᴜᴘᴘᴏʀᴛᴇᴅ ꜰᴇᴀᴛᴜʀᴇꜱ:
🎵 ᴍᴜꜱɪᴄ: ʏᴏᴜᴛᴜʙᴇ, ꜱᴘᴏᴛɪꜰʏ, ᴊɪᴏꜱᴀᴀᴠɴ, ᴀᴘᴘʟᴇ ᴍᴜꜱɪᴄ, ꜱᴏᴜɴᴅᴄʟᴏᴜᴅ
🎬 ᴠɪᴅᴇᴏ: ʏᴏᴜᴛᴜʙᴇ ᴠɪᴅᴇᴏꜱ, ᴛᴇʟᴇɢʀᴀᴍ ᴠɪᴅᴇᴏꜱ, ᴄʜᴀɴɴᴇʟ ᴠɪᴅᴇᴏꜱ

---
◎ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇꜱ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅꜱ.
"""

@Client.on_message(filters=Filter.command(["start", "help"]))
async def start_cmd(c: Client, message: types.Message):
    chat_id = message.chat_id
    bot_name = c.me.first_name
    mention = await message.mention()

    if chat_id < 0:  # Group
        welcome_text = (
            f"🎵 <b>Hello {mention}!</b>\n\n"
            f"<b>{bot_name}</b> is now active in this group.\n"
            "Here's what I can do:\n"
            "• High-quality music streaming\n"
            "• Video playback in voice chats\n"
            "• Channel video support (reply to videos)\n"
            "• Supports YouTube, Spotify, and more\n"
            "• Powerful controls for seamless playback\n\n"
            f"💬 <a href='{config.SUPPORT_GROUP}'>Need help? Join our Support Chat</a>"
        )
        reply = await message.reply_text(
            text=welcome_text,
            disable_web_page_preview=True,
            reply_markup=SupportButton,
        )

    else:  # Private chat
        bot_username = c.me.usernames.editable_username
        reply = await message.reply_photo(
            photo=config.START_IMG,
            caption=startText.format(mention, bot_name),
            reply_markup=add_me_markup(bot_username),
        )

    if isinstance(reply, types.Error):
        c.logger.warning(reply.message)


@Client.on_updateNewCallbackQuery(filters=Filter.regex(r"help_\w+"))
async def callback_query_help(c: Client, message: types.UpdateNewCallbackQuery) -> None:
    data = message.payload.data.decode()

    if data == "help_all":
        user = await c.getUser(message.sender_user_id)
        await message.answer("📚 Opening Help Menu...")
        welcome_text = (
            f"👋 <b>Hello {user.first_name}!</b>\n\n"
            f"Welcome to <b>{c.me.first_name}</b> — your ultimate music & video bot.\n"
            f"<code>Version: v{__version__}</code>\n\n"
            "💡 <b>What makes me special?</b>\n"
            "• YouTube, Spotify, Apple Music, SoundCloud support\n"
            "• Video playback in voice chats\n"
            "• Channel video support (reply to videos)\n"
            "• Advanced queue and playback controls\n"
            "• Private and group usage\n\n"
            "🔍 <i>Select a help category below to continue.</i>"
        )
        edit = await message.edit_message_caption(welcome_text, reply_markup=HelpMenu)
        if isinstance(edit, types.Error):
            c.logger.error(f"Failed to edit message: {edit}")
        return

    if data == "help_back":
        await message.answer("HOME ..")
        user = await c.getUser(message.sender_user_id)
        await message.edit_message_caption(
            caption=startText.format(user.first_name, c.me.first_name),
            reply_markup=add_me_markup(c.me.usernames.editable_username),
        )
        return

    help_categories = {
        "help_user": {
            "title": "🎧 User Commands",
            "content": (
                "<b>▶️ Playback:</b>\n"
                "• <code>/play [song]</code> — Play audio in VC\n"
                "• <code>/vplay [video]</code> — Play video in VC\n"
                "• <code>/play</code> (reply to video) — Play replied video\n"
                "• <code>/vplay</code> (reply to video) — Play replied video\n\n"
                "<b>🎬 Video Features:</b>\n"
                "• Reply to any video message with /play or /vplay\n"
                "• Channel video support\n"
                "• YouTube video URLs\n"
                "• Local video files\n\n"
                "<b>🛠 Utilities:</b>\n"
                "• <code>/start</code> — Intro message\n"
                "• <code>/help</code> — Help menu\n"
                "• <code>/ping</code> — Bot latency\n"
                "• <code>/uptime</code> — Bot uptime"
            ),
        },
        "help_admin": {
            "title": "👑 Admin Commands",
            "content": (
                "<b>🎛️ Controls:</b>\n"
                "• <code>/pause</code> — Pause playback\n"
                "• <code>/resume</code> — Resume playback\n"
                "• <code>/skip</code> — Skip current track\n"
                "• <code>/stop</code> — Stop playback\n"
                "• <code>/end</code> — Clear queue\n\n"
                "• <code>/volume [1-200]</code> — Adjust volume\n"
                "• <code>/seek [time]</code> — Seek to position\n"
                "• <code>/loop [0-3]</code> — Set loop mode\n\n"
                "<b>⚙️ Settings:</b>\n"
                "• <code>/settings</code> — Bot settings\n"
                "• <code>/reload</code> — Reload bot\n"
                "• <code>/broadcast</code> — Broadcast message"
            ),
        },
        "help_owner": {
            "title": "🔧 Owner Commands",
            "content": (
                "<b>🛠️ Maintenance:</b>\n"
                "• <code>/update</code> — Update bot\n"
                "• <code>/restart</code> — Restart bot\n"
                "• <code>/logs</code> — View logs\n"
                "• <code>/shell</code> — Execute shell command\n\n"
                "<b>📊 Stats:</b>\n"
                "• <code>/stats</code> — Bot statistics\n"
                "• <code>/users</code> — User statistics\n"
                "• <code>/chats</code> — Chat statistics\n\n"
                "<b>🔐 Access:</b>\n"
                "• <code>/addowner</code> — Add owner\n"
                "• <code>/delowner</code> — Remove owner\n"
                "• <code>/adddev</code> — Add developer"
            ),
        },
    }

    if data in help_categories:
        category = help_categories[data]
        await message.answer(f"📖 Opening {category['title']}...")
        edit = await message.edit_message_caption(
            caption=f"<b>{category['title']}</b>\n\n{category['content']}",
            reply_markup=BackHelpMenu,
        )
        if isinstance(edit, types.Error):
            c.logger.error(f"Failed to edit help message: {edit}")
        return

    await message.answer("❌ Invalid help category")
