import requests

def get_string():
    resp = requests.post("http://192.168.3.20:5000/simulate")
    return(resp.json())

resp = requests.post("http://192.168.3.20:5000/simulate")
print(resp.json())