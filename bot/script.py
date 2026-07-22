# In order for this deployment to work you need to create a .env file containing the following fields:
# BOT_TOKEN
# API_ID
# API_HASH
# DB_HOST (the DNS name in the Docker network, without port)
# DB_USER
# DB_PASS
# DB_NAME

import os
from dataclasses import asdict

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.custom import Button
import mysql.connector

from telethon.tl.types import ReplyKeyboardMarkup, KeyboardButton

load_dotenv()

#All those data are to be added in a ".env" file every deployment
botToken = os.getenv('BOT_TOKEN')
apiId = int(os.getenv('API_ID'))
apiHash = os.getenv('API_HASH')
dbHost = os.getenv('DB_HOST')
dbUser = os.getenv('DB_USER')
dbPass = os.getenv('DB_PASS')
dbName = os.getenv('DB_NAME')

db = mysql.connector.connect(
  host=dbHost,
  user=dbUser,
  password=dbPass,
  database=dbName
)

# Create the client and the session called session_master. We start the session as the Bot (using bot_token)
client = TelegramClient('./sessions/session_master', apiId, apiHash).start(bot_token=botToken)

def query(query: str):
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result[0]

# Define the /start command
@client.on(events.NewMessage(pattern='/(?i)start'))
async def start(event):
    print("io laio serpente")
    sender = await event.get_sender()
    user = await client.get_entity(sender.id)
    text = "Ciao {nome}!".format(nome=user.first_name)
    await client.send_message(user.id, text)

@client.on(events.NewMessage(pattern='/(?i)prova'))
async def start(event):
    sender = await event.get_sender()
    user = await client.get_entity(sender.id)
    text = "io laio serpente"
    await client.send_message(user.id, text)