#!/usr/bin/python3

import cgi, cgitb
import os

from telethon import TelegramClient, events, sync, errors
from telethon.tl.functions.messages import GetPollVotesRequest

import requests

form = cgi.FieldStorage()
token = form.getvalue('token')

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
#print(client.get_me().stringify())

# get Nerdberg Channel
nc = next(filter(lambda c: c.id == -1001376475914, client.get_dialogs()))
#print(nc.name)


def get_poll_msg():
	return next(filter(
			lambda m: m.poll and m.sender.first_name == 'BergBot',
			client.iter_messages(nc)
	))

# get Poll msg
poll_msg = get_poll_msg()
if poll_msg.poll.results.results == None:
	poll_msg.click(4)
	poll_msg = get_poll_msg()
	poll_msg.click(None)

total_votes = poll_msg.poll.results.total_voters
options = {a.option: {"text": a.text} for a in poll_msg.poll.poll.answers}
for result in poll_msg.poll.results.results:
	#options[result.option]["num_voters"] = result.voters
	options[result.option]["voters"] = []

try:
	user_votes = client(GetPollVotesRequest(nc.id, poll_msg.id, 0))
except errors.rpcerrorlist.PollVoteRequiredError:
	poll_msg.click(4)
	user_votes = client(GetPollVotesRequest(nc.id, poll_msg.id, 0))
	poll_msg.click(None)

voters = {u.id: {
	'username': u.username,
	'first_name': u.first_name or '',
	'last_name': u.last_name or ''}
	for u in user_votes.users}
for vid, voter in voters.items():
	if not os.path.isdir('icon_cache'):
		os.mkdir('icon_cache')
	voter['icon'] = f"icon_cache/{vid}"
	if not os.path.exists(voter['icon']) or os.path.islink(voter['icon']):
		b = client.download_profile_photo(vid, file=bytes)
		if b:
			try:
				os.unlink(voter['icon'])
			except FileNotFoundError:
				pass
			with open(voter['icon'], 'wb') as f:
				f.write(b)
		elif not os.path.exists(voter['icon']):
			os.symlink('../default_icon.png', voter['icon'])

for vote in user_votes.votes:
	options[vote.option]['voters'].append(vote.user_id)

print("Content-type: text/html\n")

print("""
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,minimum-scale=1,user-scalable=no">
<link rel="manifest" href="nerdpoll_manifest.py?%s"/>
<meta name="theme-color" content="#242e3a"/>
<meta name="description" content="NerdPoll"/>
<link rel="stylesheet" tyle="text/css" href="../nerdpoll_style.css" />
<title>NerdPoll</title>
""" % os.environ.get('QUERY_STRING', ''))

print("""
<style>
</style>

<script>
window.onload = (event) => {

	// Get the modal
	var modal = document.getElementById("vote_dialog");

	// Get the button that opens the modal
	var btn = document.getElementById("vote");

	// Get the <span> element that closes the modal
	var span = document.getElementsByClassName("close")[0];

	// When the user clicks the button, open the modal
	btn.onclick = function() {
	  modal.style.display = "block";
	}

	// When the user clicks on <span> (x), close the modal
	span.onclick = function() {
	  modal.style.display = "none";
	}

	// When the user clicks anywhere outside of the modal, close it
	window.onclick = function(event) {
	  if (event.target == modal) {
		modal.style.display = "none";
	  }
	}
};
</script>


<div id="vote_dialog" class="modal">
  <!-- Modal content -->
  <div class="modal-content">
    <span class="close">&times;</span>
	<p>
""")

for oid, option in options.items():
	print(f"<a href='nerdpoll_vote.py?token={token}&selection={int(oid)}'>{option['text']}</a>")

print("""
    </p>
  </div>
</div>
""")

door_status = requests.get("https://status.nerdberg.de/api/doorstatus/").json()["results"][0]["status"]
if door_status == 'open':
	print("<div class='door'>T&uuml;re ist offen</div>")

print(f"<h3 id='vote'>{poll_msg.poll.poll.question.replace(' ', '&nbsp;').replace('&nbsp;vor&nbsp;', '&nbsp;vor ')}</h3>")

print('<table>')
for oid, option in options.items():
	if len(option['voters']):
		voter_string='Mensch'
		if len(option['voters']) > 1:
			voter_string +='en'
		print(f"<tr class='h'><td colspan='2'>{option['text']}</td><td class='peps'>{len(option['voters'])} {voter_string}</td></tr>")
	for uid in option['voters']:
		name = (voters[uid]['first_name'] + ' ' + voters[uid]['last_name']).strip() or voters[uid]['username']
		if name != voters[uid]['username'] and voters[uid]['username']:
			name += f" ({ voters[uid]['username'] })"
		print(f"<tr><td class='imgbox'><img src='../{voters[uid]['icon']}' /></td><td colspan='2'>{ name }</td></tr>")
print('</table>')
