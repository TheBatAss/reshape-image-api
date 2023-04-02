from flask import Flask, jsonify, request
import hashlib
from PIL import Image
import urllib.request
import io

app = Flask(__name__)
PORT = 5000

FILE_FORMATS = ['jpg', 'jpeg', 'png']


@app.route('/get_image_hash', methods=['POST'])
def get_image_hash():
    image_url = request.json['image_url']
    file_ext = image_url.split('.')[-1].lower()

    if file_ext not in FILE_FORMATS:
        return jsonify({'error': 'Invalid file format. Only JPG, JPEG and PNG files are allowed.'}), 400

    image_data = urllib.request.urlopen(image_url).read()
    img = Image.open(io.BytesIO(image_data))
    image_hash = hashlib.sha256(img.tobytes()).hexdigest()
    return {'image_hash': image_hash}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
