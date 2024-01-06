import requests


class ImageUploader:
    def __init__(self, url, image_path):
        self.url = url
        self.image_path = image_path

    def upload_image(self):
        files = {'file': ('filename.png', open(self.image_path, 'rb'), 'image/png')}
        response = requests.post(self.url, files=files)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None


