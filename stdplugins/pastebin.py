"""`.paste` : Reply to a text or a file to paste it on nekobin
`.gpaste` : Reply to a paste link to get it's content."""

from telethon import events
import os
import io
import asyncio
from uniborg.util import admin_cmd
import aiohttp

class AioHttp:
    @staticmethod
    async def get_json(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.json()

    @staticmethod
    async def get_text(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.text()

    @staticmethod
    async def get_raw(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.read()

@borg.on(admin_cmd("paste ?(.*)"))
async def _(event):
    reply = await event.get_reply_message()
    if reply:
        text = reply.message
    if reply.media:
            downloaded_file_name = await borg.download_media(
                reply,
                Config.TMP_DOWNLOAD_DIRECTORY,
            )
            m_list = None
            with open(downloaded_file_name, "rb") as fd:
                m_list = fd.readlines()
            text = ""
            for m in m_list:
                text += m.decode("UTF-8") + "\r\n"
            os.remove(downloaded_file_name)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    'https://nekobin.com/api/documents',
                    json={"content": text},
                    timeout=3
            ) as response:
                key = (await response.json())["result"]["key"]
    except Exception:
        await event.edit("`Pasting failed`")
        await asyncio.sleep(2)
        await event.delete()
        return
    else:
        url = f'https://nekobin.com/{key}'
        raw_url = f'https://nekobin.com/raw/{key}'
        reply_text = '**Nekofied:**\n'
        reply_text += f' - **Link**: {url}\n'
        reply_text += f' - **Raw**: {raw_url}'
        await event.edit(
                reply_text,
                link_preview=False,
            )
            
@borg.on(admin_cmd("gpaste ?(.*)"))           
async def _(event):
    """fetches the content of a dogbin or nekobin URL."""
    reply = await event.get_reply_message()
    link = reply.message
    if not link:
        await msg(message, text="Input not found!")
        return
    await event.edit("`Getting paste content...`")
    format_view = 'https://del.dog/v/'
    if link.startswith(format_view):
        link = link[len(format_view):]
        raw_link = f'https://del.dog/raw/{link}'
    elif link.startswith("https://del.dog/"):
        link = link[len("https://del.dog/"):]
        raw_link = f'https://del.dog/raw/{link}'
    elif link.startswith("del.dog/"):
        link = link[len("del.dog/"):]
        raw_link = f'https://del.dog/raw/{link}'
    elif link.startswith("https://nekobin.com/"):
        link = link[len("https://nekobin.com/"):]
        raw_link = f'https://nekobin.com/raw/{link}'
    elif link.startswith("nekobin.com/"):
        link = link[len("nekobin.com/"):]
        raw_link = f'https://nekobin.com/raw/{link}'
    else:
        await event.edit("Is that even a paste url?")
        return
    resp = await AioHttp().get_text(raw_link)
    if len(str(resp)) > 4096:
        with io.BytesIO(str.encode(resp)) as out_file:
            out_file.name = "gpaste.txt"
            await event.client.send_file(event.chat_id, out_file)
    else:
       await event.edit(
        f"**URL content** :\n`{resp}`")
