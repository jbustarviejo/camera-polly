import os, boto3
from pydub import AudioSegment
from pydub.playback import play
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
    people = glob.glob('know_people/*.jpg')
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
        person_name = re.search('know_people/(.+?).jpg', person)[1]
        file = open(person, 'rb')

        # object = s3.Object('keylab', "face_recognition/"+person)
        # ret = object.put(Body=file,Metadata={'FullName': person_name})

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

    recognized = rekognition.search_faces_by_image(
		Image={
			"Bytes": b
        },CollectionId="keynos"
    )

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

s3 = session.resource("s3")
polly = session.client("polly")
rekognition = session.client("rekognition")

# list_faces()

uploadAll()
detected_faces = detectFaceFromImage()
for face in detected_faces:
    speak("He detectado a "+face)
