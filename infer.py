from picamera import PiCamera
import requests

def infer(d):
    camera = PiCamera()
    camera.capture("test.jpg")
    file_byte = open("test.jpg", "rb")
    camera.close()
    d = str(d)
    resp = requests.post("http://192.168.3.20:5000/predict", files={"file": file_byte, "coord":d})
    return resp.json()

if __name__ == "__main__":
    response = infer({"x": 2, "y":3})
    print(response)
