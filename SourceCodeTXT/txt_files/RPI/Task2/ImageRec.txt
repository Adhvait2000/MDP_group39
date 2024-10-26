
from queue import Queue
import requests
from picamera import PiCamera
from time import sleep
import time
class ImageRecInterface:
    def __init__(self):
        self.URL = 'http://192.168.39.21:5000/image'

    def post(self, path):
        direction = 'L'
        try:
            # Open the image file
            image_file = open(path, 'rb')
            files = {'file': image_file}
            response = requests.post(self.URL, files=files)
            json_data = response.json()
            print(json_data)
            if(json_data == "38"):
                direction = 'R'
            print("Directing to:" , direction)
            return direction

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return e


    def get_image(self):
        # capture img to img_pth
        timestamp = round(time.time())
        img_pth = f"img_{timestamp}.jpg"
        camera = PiCamera()
        camera.start_preview()
        sleep(2)
        camera.capture(img_pth)
        camera.stop_preview()
        camera.close()
        return img_pth
