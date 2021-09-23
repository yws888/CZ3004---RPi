from picamera import PiCamera
import requests

def infer():
    camera = PiCamera()
    camera.capture("test.jpg")
    file_byte = open("test.jpg", "rb")
    camera.close()
    resp = requests.post("http://192.168.3.20:5000/predict", files={"file": file_byte})
    return resp.json()
