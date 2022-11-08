#!/usr/bin/python3

import os
import cgi, cgitb

from telethon import TelegramClient, events, sync, errors
from telethon.tl.functions.messages import GetPollVotesRequest

MY_TOKEN = "correcthorsebatterystaple"

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = 20661388
api_hash = '47c79ec8bf00f87eecfe242f9863d728'

client = TelegramClient('mysession1_np', api_id, api_hash)

myevents = []
@client.on(events.NewMessage)
def my_event_handler(event):
	myevents.append(event)

client.start()

# get Nerdberg Channel
nc = next(filter(lambda c: c.id == -1001376475914, client.get_dialogs()))

def get_poll_msg():
	return next(filter(
			lambda m: m.poll and m.sender.first_name == 'BergBot',
			client.iter_messages(nc)
	))

form = cgi.FieldStorage()
selection = form.getvalue('selection')
if selection:
	selection = int(selection)
token = form.getvalue('token')
if token != MY_TOKEN:
	print("Content-type: text/plain\n\nInvalid Token\n")
else:
	# get Poll msg
	poll_msg = get_poll_msg()
	poll_msg.click(selection)

	print("Status: 302 Found")
	print(f"Location: nerdpoll.py?token={token}")
	print("Content-type: text/html\n")
	print("Redirecting...")
	print(f"<meta http-equiv=\"refresh\" content=\"0; url=nerdpoll.py?token={token}\">")
