#!/usr/bin/python

'''
# crontab
*/2 * * * * export DISPLAY=:0; /usr/bin/python ~/git/john/minas/scripts/chat_logs.py >> /var/log/john/chat_logger.log 2>&1

'''
import pyautogui
import pyperclip
import difflib

import os
from os.path import expanduser

from datetime import datetime
from time import sleep

import pygtk
pygtk.require('2.0')
import gtk
import wnck
import re
import sys
import time

import subprocess
from functools import partial


home = expanduser("~")
chat_home_dir = "{}/git/john/minas/chat_logs".format(home)
chatlog_cmd = partial(subprocess.check_output, cwd=chat_home_dir, shell=True)


MIN_IDLE = 5000
MAX_TRIES = 10
MAX_COMMIT_MIN = 60

rooms = [
'thinkScript Lounge',
'Trader Lounge'
]

# commit chat logs
def commit_chat_logs():
	NO_CHANGES = 'nothing to commit, working tree clean'
	status = chatlog_cmd('git status')
	print(status)

	if NO_CHANGES in status:
		print("No changes to commit.")
	else:

		# time since last commit
		cmd = "(git log --pretty=format:'%at' -1)"
		last_log = chatlog_cmd(cmd)

		last_commit_min = ( int(time.time()) - int(last_log) ) / 60
		if last_commit_min > MAX_COMMIT_MIN:
			# git commit
			cmds = [
				'git add .',
				'git commit -m "autocommit chat logs"',
				'for i in `git remote `; do git push $i master; done'
			]
			for c in cmds:
				res = chatlog_cmd(c)
				print(res)

		else:
			print("Not committing yet. {} "
				  "minutes since last commit." \
				  .format(last_commit_min))


def get_chat_logs():
	active_window = None
	room_windows = {}
	screen = wnck.screen_get_default()
	while gtk.events_pending():
		gtk.main_iteration()
		windows = screen.get_windows()
		active_window = screen.get_active_window()
		for w in windows:
			for room in rooms:
				titlePattern = re.compile('.*{}.*'.format(room))
				if titlePattern.match(w.get_name()):
					room_windows[room] = w

	for room, w in room_windows.iteritems():
		print(w.get_name())
		print(w.get_pid())
		w.activate(0)
		x, y, width, height = w.get_client_window_geometry()

		pyautogui.click(x=x+20, y=y+height/2)
		sleep(.2)
		pyautogui.hotkey('ctrl', 'a')
		sleep(.5)
		pyautogui.hotkey('ctrl', 'c')
		sleep(.5)
		data = pyperclip.paste()
		# print("data: {}".format(data))

		filename = "{r}-{d}.txt".format(
			r=room.replace(' ', ''),
			d=datetime.now().strftime("%Y%m%d")
			)

		folder = '{c}/{r}'.format(c=chat_home_dir, r=room)
		if not os.path.exists(folder):
		    os.mkdir(folder)

		old_data = ''
		try:
			chat_log = '{dir}/{f}'.format(
				dir=folder,
				f=filename)
			with open(chat_log, 'r') as f:
				old_data = f.read()
		except IOError:
			pass

		if old_data:
			diff = difflib.ndiff(old_data.split('\n'), data.split('\n'))
			changes = [l[2:] for l in diff if l.startswith('+ ') or l.startswith('- ')]
			changes = [x for x in changes if x != '']
			print("{} new lines".format(len(changes)))
			if len(changes) > 0:
				data = '\n'.join(changes)
			else:
				continue
		else:
			print("Writing new file.")

		mode = 'a' if os.path.exists(chat_log) else 'w'
		with open(chat_log, mode) as f:
			f.write(data)

		# deduplicate to make sure difflib didnt mess up 
		cmd = "awk '!seen[$0]++ == 1' '{f}' > '{f}.tmp' && mv '{f}.tmp' '{f}' ".format(f=chat_log)
		print(cmd)
		out = subprocess.check_output(
	           [cmd],
				cwd=chat_home_dir,
				shell=True
				)
		print(out)
		sleep(1)

	active_window.activate(0)





def get_chat_logs_on_idle():
	for tries in xrange(0, MAX_TRIES):
		if tries >= MAX_TRIES:
			print("Too busy to run.")
			sys.exit(1)
		idle = subprocess.check_output(['xprintidle'])
		idle = int(idle)
		if idle > MIN_IDLE:
			get_chat_logs()
			return 1
		else:
			print("Idle at {}. Waiting for greater than {}".format(
				idle, MIN_IDLE))
		sleep(3)

	print("Computer is not idle. Not running for now.")
	return 0


def main():
	result = get_chat_logs_on_idle()
	if result == 1:
		commit_chat_logs()


if __name__ == '__main__':
	main()