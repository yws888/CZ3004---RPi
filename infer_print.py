from picamera import PiCamera
import requests

camera = PiCamera()
camera.capture("test.jpg")
file_byte = open("test.jpg", "rb")

resp = requests.post("http://192.168.3.20:5000/predict", files={"file": file_byte})

print(resp.json())
