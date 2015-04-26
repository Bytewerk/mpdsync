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
	global selfMPD
	global bingoMPD
	oldVol = int(selfMPD.status()["volume"])
	#fade out
	for vol in range(oldVol, 1, -1):
		selfMPD.setvol(vol)
		sleep(0.05)

	selfMPD.clear()
	selfMPD.addid(newSong, 0)
	selfMPD.play(0)
	bingoMPDPlayTime = bingoMPD.status()["time"].split(":")[0]
	selfMPD.seekcur(bingoMPDPlayTime)

	#fade in
	for vol in range(0, oldVol, 1):
		selfMPD.setvol(vol)
		sleep(0.05)


def connect():
	print("Connecting...")
	global bingoMPD
	global selfMPD
	bingoMPD = MPDClient()
	bingoMPD.connect("music.bingo", 6600)
	selfMPD = MPDClient()
	selfMPD.connect("localhost", 6600)
	print("Connected!")

def updateSong(newSong):
	global bingoMPD
	global selfMPD
	try:
		selfMPD.delete(0)
	except:
		pass
	selfMPD.addid(newSong, 0)
	selfMPD.play(0)

def close():
	try:
		bingoMPD.close()
		bingoMPD.disconnect()
		selfMPD.close()
		selfMPD.disconnect()
	except:
		print("got an exception in close()")
		pass

print("Setting up GPIOs")
setupGPIO()
connect()
print("Fetching remote song")
currentSong = bingoMPD.currentsong().get("file")
oldSong = currentSong
print("Clearing old playlist")
selfMPD.clear()
print("Playing remote song: " + currentSong)
if len(currentSong) > 0:
	updateSong(currentSong)
print("Sync playtime to remote MPD")
bingoMPDPlayTime = bingoMPD.status()["time"].split(":")[0]
selfMPD.seekcur(bingoMPDPlayTime)

currentSwitchState = GPIO.input(7) # True == Sync
oldSwitchState = currentSwitchState
while True:
	# If the song has changed, add it to position 0 and play it
	if currentSong != oldSong and currentSwitchState == 1:
		if len(currentSong) > 0:
			print("Remote song changed, syncing...")
			updateSong(currentSong)
		else:
			print("Remote song is empty, skipping...")
		oldSong = currentSong

	# If the switch gets toggled from "custom play mode" to "sync mode" then fade over to the current playing song
	if (currentSwitchState != oldSwitchState):
		if (currentSwitchState == 1):
			print("Switch changed to sync mode, going to fade now...")
			fadeOver(currentSong)
			oldSwitchState = currentSwitchState
		else:
			print("Switch changed to manual mode, good luck!")
			oldSwitchState = currentSwitchState

	currentSong = bingoMPD.currentsong().get("file")
	currentSwitchState = GPIO.input(7)
close()
