import os, boto3
from pydub import AudioSegment
from pydub.playback import play
from time import sleep
import glob
import re

from picamera import picamera
import face_recognition

polly = connectToPolly()
camera = picamera.PiCamera()

def connectToPolly():
    boto3.session.Session(profile_name="apilambda")
    boto3.setup_default_session(profile_name="apilambda")
    return boto3.client('polly')

def speak(polly, text, format='mp3', voice='Conchita'):
    resp = polly.synthesize_speech(OutputFormat=format, Text=text, VoiceId=voice)
    soundfile = open('sound.mp3', 'wb')
    soundBytes = resp['AudioStream'].read()
    soundfile.write(soundBytes)
    soundfile.close()

    mysong = AudioSegment.from_mp3("sound.mp3")
    play(mysong)
    os.remove('sound.mp3')

def capture():
    try:
        camera.start_preview()
        camera.capture('capture.jpg')
        camera.stop_preview()
    finally:
        camera.close()

def recognize():
    people = glob.glob('know_people/*.jpg')
    people_in_capture=[]
    for person in people:
        person_name = re.search('know_people/(.+?).jpg', person)

        known_image = face_recognition.load_image_file(person)
        unknown_image = face_recognition.load_image_file("capture.jpg")

        try:
            known_image_encoding = face_recognition.face_encodings(known_image)[0]
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        except IndexError:
            continue

        results = face_recognition.compare_faces([known_image_encoding], unknown_encoding)
        if(results):
            people_in_capture.append(person_name)
    return people_in_capture

def loop():
    capture()
    people_in_picture = recognize()
    for person in people_in_picture:
        speak(polly, "Hola "+person)
    sleep(3)

loop()
