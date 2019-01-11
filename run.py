import os, boto3
from pydub import AudioSegment
from pydub.playback import play
from picamera import PiCamera
from time import sleep
import glob
import re

session = boto3.session.Session(profile_name="keylab")

def speak(text, format='mp3', voice='Conchita'):
    resp = polly.synthesize_speech(OutputFormat=format, Text=text, VoiceId=voice)
    soundfile = open('sound.mp3', 'wb')
    soundBytes = resp['AudioStream'].read()
    soundfile.write(soundBytes)
    soundfile.close()

    mysong = AudioSegment.from_mp3("sound.mp3")
    play(mysong)
    os.remove('sound.mp3')

def uploadAll():
    people = glob.glob('know_people/*.png')
    people_in_capture=[]

    try:
        response = rekognition.delete_collection(
            CollectionId='keynos'
        )
    except Exception:
        print("Keynos collection didn't exist")
    try:
        rekognition.create_collection(CollectionId='keynos')
    except Exception:
        print("Keynos collection already created")


    for person in people:
        person_name = re.search('know_people/(.+?).png', person).groups()
        if not person_name:
            continue
        person_name = person_name[0]
        file = open(person, 'rb')

        print("Uploading "+str(person_name)+ ": face_recognition/"+person)
        
        object = s3.Object('keylab', "face_recognition/"+person)
        ret = object.put(Body=file,Metadata={'FullName': person_name})

        response = rekognition.index_faces(CollectionId="keynos", Image={
            'S3Object': {
                'Bucket': 'keylab',
                'Name': "face_recognition/"+person,
                }
            },
            ExternalImageId=person_name
        )

def detectFaceFromImage():
    with open("capture.jpg", "rb") as imageFile:
      f = imageFile.read()
      b = bytearray(f)

    try:
        recognized = rekognition.search_faces_by_image(
            Image={
                "Bytes": b
            },CollectionId="keynos",
            MaxFaces=123
        )
    except:
        return []
    print(recognized)

    detected_faces = []

    for face in recognized["FaceMatches"]:
        print("Face: "+str(face))
        detected_faces.append(face["Face"]["ExternalImageId"])
    return detected_faces

def list_faces():
    response = rekognition.list_faces(
        CollectionId='keynos',
    )
    print(response)

def routine():
    while(True):
        print("Taking photo")
        camera.capture('capture.jpg', resize=(600, 400))
        print("Taked!")

        detected_faces = detectFaceFromImage()
        print(detected_faces)
        for face in detected_faces:
            speak("Hola "+face)
        print("Waiting 2 secs...")
        sleep(2)

s3 = session.resource("s3")
polly = session.client("polly")
rekognition = session.client("rekognition")
camera = PiCamera()


#list_faces()

#uploadAll()

routine()

