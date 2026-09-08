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
from time import sleep
from xml.etree.ElementTree import tostring

import emoji
import pymysql
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.custom import Button

load_dotenv()

#All those data are to be added in a ".env" file every deployment
botToken = os.getenv('BOT_TOKEN')
apiId = int(os.getenv('API_ID'))
apiHash = os.getenv('API_HASH')
dbHost = os.getenv('DB_HOST')
dbUser = os.getenv('DB_USER')
dbPass = os.getenv('DB_PASS')
dbName = os.getenv('DB_NAME')

db = pymysql.connect(
  host="localhost",
  user=dbUser,
  password=dbPass,
  database=dbName
)

# Create the client and the session called session_master. We start the session as the Bot (using bot_token)
client = TelegramClient('./sessions/session_master', apiId, apiHash).start(bot_token=botToken)

messagesToBeDeleted = []

def query(query: str, params):
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    if result.__len__() == 0:
        return []
    else:
        return result[0]

# Define the /start command
@client.on(events.NewMessage(pattern='(?i)^/start'))
async def start(event):
    sender = await event.get_sender()
    user = await client.get_entity(sender.id)

    async with client.conversation(event.chat_id, timeout=20) as conv:

        keyboard = [
            [
                Button.inline("ℹ️ Informazioni", b"info"),
                Button.inline("📝 Crea una nuova lista", b"newList"),
            ]
        ]

        text = "Ciao {nome}! Benvenut* in ListBot, come posso aiutarti?".format(nome=user.first_name)
        messagesToBeDeleted.append(await client.send_message(event.chat.id, text, buttons=keyboard))

@client.on(events.callbackquery.CallbackQuery(data=b"info"))
@client.on(events.NewMessage(pattern='(?i)^/info'))
async def start(event):
    sender = await event.get_sender()
    user = await client.get_entity(sender.id)

    async with client.conversation(event.chat_id, timeout=20) as conv:
        keyboard = [
            [
                Button.inline("📖 Mostra le tue liste", b"showLists"),
                Button.inline("📝 Crea una nuova lista", b"newList"),
            ]
        ]

        text = "Ciao {nome}! Benvenut* in ListBot, un semplice bot Telegram OpenSource per gestire delle liste.\nPuoi trovare la repository su GitHub a questo [link](https://github.com/mirrorleos/listBot).".format(
            nome=user.first_name)
        messagesToBeDeleted.append(await client.send_message(event.chat.id, text, buttons=keyboard))

@client.on(events.callbackquery.CallbackQuery(data=b"newList"))
@client.on(events.NewMessage(pattern=r'(?i)^/newList'))
async def newList(event):
    await client.delete_messages(event.chat.id, messagesToBeDeleted)
    messagesToBeDeleted.clear()

    if isinstance(event, events.CallbackQuery.Event):
        await event.answer()
    else:
        messagesToBeDeleted.append(event.message)

    async with client.conversation(event.chat_id, timeout=60) as conv:

        messagesToBeDeleted.append(await conv.send_message("Come vuoi chiamare la lista?"))

        response = await conv.get_response()
        messagesToBeDeleted.append(response)
        name = response.text[:30]
        creationDate = response.date.isoformat()
        listProperty = event.chat.id

        cursor = db.cursor()
        cursor.execute("insert into lists(property, creationDate, name) values (%s, %s, %s)",(listProperty, creationDate, name))
        db.commit()

        #query(f"insert into lists(property, creationDate, name) values (%s, %s, %s)",(listProperty, creationDate, name))

        keyboard = [
            [
                Button.inline("📝 Crea un nuovo elemento", f"newElement_{cursor.lastrowid}"),
            ]
        ]

        messagesToBeDeleted.append(await conv.send_message(
            f"Perfetto! Ho creato la lista \"{name}\". Usa il tasto qui sotto se vuoi creare un nuovo elemento in questa lista!",
            buttons=keyboard))

@client.on(events.callbackquery.CallbackQuery(pattern=b"newElement_*"))
@client.on(events.NewMessage(pattern=r'(?i)^/newElement'))
async def newElement(event):
    await client.delete_messages(event.chat.id, messagesToBeDeleted)
    messagesToBeDeleted.clear()

    listId = None
    elementName = ""
    done = False
    assignee = None

    if isinstance(event, events.CallbackQuery.Event):
        await event.answer()
        listId = (event.data.decode("utf-8").split("_")[1])
    else:
        messagesToBeDeleted.append(event.message)

    async with client.conversation(event.chat_id, timeout=60) as conv:

        if listId is None:
            cursor = db.cursor()
            cursor.execute("select * from lists where property = %s", (event.chat_id))

            keyboard = []

            for row in cursor.fetchall():
                keyboard.append([Button.text(f"📋 {row[3]}")])

            keyboard.append([Button.text(f"↩️ Annulla")])

            messagesToBeDeleted.append(await conv.send_message("A quale lista vuoi aggiungere il nuovo elemento?", buttons=keyboard))

            response = await conv.get_response()
            response = emoji.replace_emoji(response.text, replace="").strip()

            if response == "Annulla" :

            else:
                listName = conv.get_response()
                print(listId)

        else:
            messagesToBeDeleted.append(await conv.send_message("Qual'è il titolo del tuo elemento?"))

            response = await conv.get_response()
            messagesToBeDeleted.append(response)
            elementName = response.text[:100]
            creationDate = response.date
            listProperty = event.chat.id
            query(f"insert into lists(property, creationDate, name) values (%s, %s, %s)",
                  (listProperty, creationDate, name))

            keyboard = [
                [
                    Button.inline("📝 Crea un nuovo elemento", b"newElement"),
                ]
            ]

            messagesToBeDeleted.append(await conv.send_message(
                f"Perfetto! Ho creato la lista \"{name}\". Usa il tasto qui sotto se vuoi creare un nuovo elemento in questa lista!",
                buttons=keyboard))

@client.on(events.callbackquery.CallbackQuery(data=b"Cancel"))
@client.on(events.NewMessage(pattern=r'(?i)^/Cancel'))
async def cancel(event):
    await client.delete_messages(event.chat.id, messagesToBeDeleted)
    messagesToBeDeleted.clear()


if __name__ == '__main__':
    print("Il bot è stato avviato con successo!")
    client.run_until_disconnected()