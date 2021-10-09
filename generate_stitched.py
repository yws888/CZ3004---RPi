import requests

def generate_stitched():
    resp = requests.get("http://192.168.3.20:5000/get_tiled")
    return resp.json()

if __name__ == "__main__":
    response = generate_stitched()
    print(response)
