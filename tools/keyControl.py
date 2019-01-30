import requests
import readchar.readchar
import readchar.key


def getch():
  import sys, tty, termios
  old_settings = termios.tcgetattr(0)
  new_settings = old_settings[:]
  new_settings[3] &= ~termios.ICANON
  try:
    termios.tcsetattr(0, termios.TCSANOW, new_settings)
    ch = sys.stdin.read(1)
  finally:
    termios.tcsetattr(0, termios.TCSANOW, old_settings)
  return ch

url = "http://127.0.0.1:5000/status"

while True:
	querystring=''
	char = readchar.readkey()
	print(char)
	if char == ('q'):
		break
	elif char == readchar.key.RIGHT:
		print('right')
		querystring = {"move":"right"}
	elif char == readchar.key.LEFT:
		querystring = {"move":"left"}
	elif char == readchar.key.UP:
		querystring = {"move":"up"}
	elif char == readchar.key.DOWN:
		querystring = {"move":"down"}
	elif char == 'c':
		querystring = {"reset":"true"}
	print('ifover')
	response = requests.request("POST", url,  params=querystring)
	print('responseover')
	print(response.text)

