import os, json, time, requests
import google.oauth2.credentials
from PIL import Image
#import RPi.GPIO as GPIO
from natsort import natsorted
from threading import Thread, Event
from google.assistant.library import Assistant
from google.assistant.library.event import EventType
#from subprocess import call

#############
### SETUP ###
#############

### ASSISTANT SETUP ###
button_pin = 14
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(led_pin, GPIO.OUT)
#GPIO.setup(button_pin, GPIO.IN)
muted = False
device_model_id = "YourDeviceModelID"
### SETUP FOR MATRIX ###
path = "PixelArt/"
clear = Event() # --> you should start clearing
clean = Event() # --> clearing finished, ready for next image || like: already in use? yes or no
clean.set() 
url = "http://IPOfTheESP8266"


###############
### MEHTODS ###
###############

### MATRIX ###
def show_image(name):
    clean_matrix()
    img_data = None
    with Image.open(path + name + ".png") as img:
        img_data = [i[:3] for i in img.getdata()]
    r = requests.post(url, data={"data": img_data, "brightness": 10})

def show_play_animation(name, path):
    clean_matrix()
    frames, delays, path = [], [], path + "animation/" + name
    files = os.listdir(path)
    files = natsorted(files)
    for file in files:
        if file.endswith(".png"):
            with Image.open(path + "/" + file) as frame:
                frames.append([i[:3] for i in img.getdata()])
        elif file.endswith(".json"):
            with open(path + "/" + file) as f:
                data = json.load(f)
            if data["delay"]:
                for i in range(len(files)):
                    delays.append(data["delay"])
            elif data["delays"]:
                delays.append(["delays"])
        else:
            print("Unknown File found!")
    display = Thread(target=display_animation, args=(frames, delays, clear, clean))
    clean.clear()
    display.start()                               

def clean_matrix():
    clear.set()
    clean.wait()
    clear.clear()

def display_animation(frames, delays, stop_event, finish_event):
    while not stop_event.is_set():
        for e in range(len(frames)):
            frame = frames[e]
            r = requests.post(url, data={"data": frame, "brightness": 10})
            time.sleep(delays[e] / 1000) # Delay is in "ms"; /1000 converts it so "s"
    finish_event.set()
    print("thread end 1")

### ASSISTANT ###
def mute(assistant):

  global muted
  while True:
    #GPIO.wait_for_edge(button_pin, GPIO.RISING)
    time.sleep(.5)
    print('button')
    muted = not muted
    assistant.set_mic_mute(muted)

def process_event(event, assistant):

  if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
    #call(["mpg123", "ding.mp3"])
    print("Bitte sprechen Sie jetzt.")
  elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
    command = event.args['text']
    print("Antworte")

    if command == 'turn LED on':
      assistant.stop_conversation()
      #GPIO.output(led_pin, True)
      print("Turn LED on")
    elif command == 'turn LED off':
      assistant.stop_conversation()
      #GPIO.output(led_pin, False)
      print("turn LED off")
    elif "show" in command:
        print("show image")
        command = command.split(" ")
        show_image(command[1])
        assistant.stop_conversation()
    elif "play animation" in command:
        print("play animation")
        command = command.split(" ")
        show_play_animation(command[2], path)
        assistant.stop_conversation()

############
### MAIN ###
############

with open("/home/pi/.config/google-oauthlib-tool/credentials.json",'r') as f:

  credentials = google.oauth2.credentials.Credentials(
    token=None,**json.load(f)
  )

  with Assistant(credentials, device_model_id) as assistant:
    #button_thread = Thread(target=mute, args=(assistant,))
    #button_thread.start()

    print("Warte auf Hotword")
    for event in assistant.start():
      process_event(event, assistant)

