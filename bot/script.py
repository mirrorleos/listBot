# In order for this deployment to work you need to create a .env file containing the following fields:
# BOT_TOKEN
# API_ID
# API_HASH
# DB_HOST (the DNS name in the Docker network, without port)
# DB_USER
# DB_PASS
# DB_NAME
import asyncio
import os
from dataclasses import asdict

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.custom import Button
#import mysql.connector

load_dotenv()

#All those data are to be added in a ".env" file every deployment
botToken = os.getenv('BOT_TOKEN')
apiId = int(os.getenv('API_ID'))
apiHash = os.getenv('API_HASH')
dbHost = os.getenv('DB_HOST')
dbUser = os.getenv('DB_USER')
dbPass = os.getenv('DB_PASS')
dbName = os.getenv('DB_NAME')

#db = mysql.connector.connect(
#  host=dbHost,
#  user=dbUser,
#  password=dbPass,
#  database=dbName
#)

# Create the client and the session called session_master. We start the session as the Bot (using bot_token)
client = TelegramClient('./sessions/session_master', apiId, apiHash).start(bot_token=botToken)

messagesToBeDeleted = []

#def query(query: str):
#    cursor = db.cursor()
#    cursor.execute(query)
#    result = cursor.fetchall()
#    return result[0]

# Define the /start command
@client.on(events.NewMessage(pattern='(?i)^/start'))
async def start(event):
    sender = await event.get_sender()
    user = await client.get_entity(sender.id)

    try:
        async with client.conversation(event.chat_id, timeout=20) as conv:

            keyboard = [
                [
                    Button.inline("ℹ️ Informazioni", b"info"),
                    Button.inline("📝 Crea una nuova lista", b"newList"),
                ]
            ]

            text = "Ciao {nome}! Benvenut* in ListBot, come posso aiutarti?".format(nome=user.first_name)
            messagesToBeDeleted.append(await client.send_message(user.id, text, buttons=keyboard))

    except asyncio.exceptions.TimeoutError:
        return

    finally:
        await asyncio.sleep(10)
        await client.delete_messages(event.chat.id, messagesToBeDeleted)
        messagesToBeDeleted.clear()


@client.on(events.callbackquery.CallbackQuery(data=b"newList"))
@client.on(events.NewMessage(pattern=r'(?i)^/newList'))
async def newList(event):
    await client.delete_messages(event.chat.id, messagesToBeDeleted)
    messagesToBeDeleted.clear()

    try:
        if isinstance(event, events.CallbackQuery.Event):
            await event.answer()
        else:
            messagesToBeDeleted.append(event.message)

        async with client.conversation(event.chat_id, timeout=60) as conv:
            messagesToBeDeleted.append(await conv.send_message("Come vuoi chiamare la lista?"))

            response = await conv.get_response()
            messagesToBeDeleted.append(response)
            name = response.text

            messagesToBeDeleted.append(await conv.send_message(f"Perfetto! Ho creato la lista \"{name}\"."))

    except asyncio.exceptions.TimeoutError:
        messagesToBeDeleted.append(await event.respond("⏳ Tempo scaduto! Procedura annullata."))

    finally:
        await asyncio.sleep(10)
        await client.delete_messages(event.chat.id, messagesToBeDeleted)
        messagesToBeDeleted.clear()

if __name__ == '__main__':
    print("Il bot è stato avviato con successo!")
    client.run_until_disconnected()