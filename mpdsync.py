from mpd import MPDClient
from time import sleep
import RPi.GPIO as GPIO

currentSong = None
bingoMPD = None
selfMPD = None

def setupGPIO():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(7, GPIO.IN)

def fadeOver(newSong):
	oldVol = int(selfMPD.status()["volume"]
	selfMPD.addid(newSong, 1)
	#fade out
	for vol in range(oldVol, 1, -1):
		selfMPD.setvol(vol)
		sleep(0.1)

	selfMPD.playid(1)
	bingoMPDPlayTime = bingoMPD.status()["time"].split(":")[0]
	selfMPD.seekcur(bingoMPDPlayTime)

	#fade in
	for vol in range(0, oldVol, 1):
		selfMPD.setvol(vol)
		sleep(0.1)


def connect():
	global bingoMPD
	global selfMPD
	bingoMPD = MPDClient()
	bingoMPD.connect("music.bingo", 6600)
	selfMPD = MPDClient()
	selfMPD.connect("localhost", 6600)

def updateSong():
	print("don't call me anymore, fool!")
	return
	if GPIO.input(7):
		# Sync is on
		global currentSong
		try:
			try:
				selfMPD.delete(0)
			except:
				pass
			currentSong = bingoMPD.currentsong()["file"]
			selfMPD.addid(currentSong, 0)
			print("updated song")
			selfMPD.play(0)
		except:
			print("got an exception in updateSong()")
			close()
			connect()
			updateSong()
	else:
		# Sync is off
		pass

def close():
	try:
		bingoMPD.close()
		bingoMPD.disconnect()
		selfMPD.close()
		selfMPD.disconnect()
	except:
		print("got an exception in close()")
		pass

setupGPIO()
connect()
updateSong()
currentSong = bingoMPD.currentsong()["file"]
oldSong = currentSong
currentSwitchState = GPIO.input(7) # True == Sync
oldSwitchState = currentSwitchState
while True:
	# If the song has changed, add it to position 0 and play it
	if currentSong != oldSong:
		try:
			selfMPD.delete(0)
		except:
			pass
		selfMPD.addid(currentSong, 0)
		selfMPD.play(0)
		oldSong = currentSong
	currentSong = bingoMPD.currentsong()["file"]

	# If the switch gets toggled from "custom play mode" to "sync mode" then fade over to the current playing song
	if currentSwitchState != oldSwitchState and currentSwitchState:
		fadeOver(currentSong)
		oldSwitchState = currentSwitchState
	currentSwitchState = GPIO.input(7)

close()
