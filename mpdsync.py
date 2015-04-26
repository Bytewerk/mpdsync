from mpd import MPDClient
import RPi.GPIO as GPIO

currentSong = None
bingoMPD = None
selfMPD = None

def setupGPIO():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(7, GPIO.IN)

def connect():
	global bingoMPD
	global selfMPD
	bingoMPD = MPDClient()
	bingoMPD.connect("music.bingo", 6600)
	selfMPD = MPDClient()
	selfMPD.connect("localhost", 6600)

def updateSong():
	if GPIO.input(7):
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
while True:
	print("waiting for songchange")
	updateSong()
	bingoMPD.idle("player")
close()
