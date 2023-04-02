from flask import Flask, jsonify, request, send_file
import hashlib
from PIL import Image
import urllib.request
import io
import cv2
import numpy as np

app = Flask(__name__)
PORT = 5000

VALID_IMAGE_FORMATS = ['jpg', 'jpeg', 'png']


@app.route('/get_image_hash', methods=['POST'])
def get_image_hash():
    # Validate required fields are present
    if 'image_url' not in request.json:
        return jsonify({'error': "Missing property 'image_url'"}), 400

    image_url = request.json['image_url']

    # Validate image format
    file_ext = image_url.split('.')[-1].lower()
    if file_ext not in VALID_IMAGE_FORMATS:
        return jsonify({'error': 'Invalid file format. Only JPG, JPEG and PNG files are allowed.'}), 400

    # Load image, convert to binary and get the hash
    image_data = urllib.request.urlopen(image_url).read()
    img = Image.open(io.BytesIO(image_data))
    image_hash = hashlib.sha256(img.tobytes()).hexdigest()
    return {'image_hash': image_hash}


@app.route('/center_crop', methods=['POST'])
def center_crop():
    # Validate required fields are present
    if 'image_url' not in request.json:
        return jsonify({'error': "Missing property 'image_url'"}), 400
    if 'width' not in request.json:
        return jsonify({'error': "Missing property 'width'"}), 400
    if 'height' not in request.json:
        return jsonify({'error': "Missing property 'height'"}), 400

    image_url = request.json['image_url']
    width = request.json['width']
    height = request.json['height']

    # Validate image format
    file_ext = image_url.split('.')[-1].lower()
    if file_ext not in VALID_IMAGE_FORMATS:
        return jsonify({'error': 'Invalid file format. Only JPG, JPEG and PNG files are allowed.'}), 400

    # Load image and convert into binary
    image_data = urllib.request.urlopen(image_url).read()
    img = Image.open(io.BytesIO(image_data))

    # Validate that new width and height is equal or less than original
    img_width, img_height = img.size
    if width > img_width:
        return jsonify({'error': 'Width is larger than original image.'}), 400
    if height > img_height:
        return jsonify({'error': 'Height is larger than original image.'}), 400

    # Calculate new image size
    left = (img_width - width) / 2
    top = (img_height - height) / 2
    right = (img_width + width) / 2
    bottom = (img_height + height) / 2

    # Ensure that image is in RGB mode and crop it (crop only works with RGB and grayscale)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.crop((left, top, right, bottom))

    # Convert into JPEG
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='JPEG')
    output_buffer.seek(0)

    return send_file(output_buffer, mimetype='image/jpeg')


@app.route('/get_SIFT_difference', methods=['POST'])
def get_SIFT_difference():
    # Validate required fields are present
    if 'image_url_1' not in request.json:
        return jsonify({'error': "Missing property 'image_url_1'"}), 400
    if 'image_url_2' not in request.json:
        return jsonify({'error': "Missing property 'image_url_2'"}), 400

    image_url_1 = request.json['image_url_1']
    image_url_2 = request.json['image_url_2']

    # Validate image format
    file_ext_1 = image_url_1.split('.')[-1].lower()
    file_ext_2 = image_url_2.split('.')[-1].lower()
    if file_ext_1 not in VALID_IMAGE_FORMATS:
        return jsonify({'error': 'Invalid file format for image 1. Only JPG, JPEG and PNG files are allowed.'}), 400
    if file_ext_2 not in VALID_IMAGE_FORMATS:
        return jsonify({'error': 'Invalid file format for image 2. Only JPG, JPEG and PNG files are allowed.'}), 400

    # Load images and convert into binary
    image_data_1 = io.BytesIO(urllib.request.urlopen(image_url_1).read())
    img1 = cv2.imdecode(np.frombuffer(
        image_data_1.read(), np.uint8), cv2.IMREAD_COLOR)

    image_data_2 = io.BytesIO(urllib.request.urlopen(image_url_2).read())
    img2 = cv2.imdecode(np.frombuffer(
        image_data_2.read(), np.uint8), cv2.IMREAD_COLOR)

    # Convert images to grayscale
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Initialize SIFT detector
    sift = cv2.SIFT_create()

    # Find key points and descriptors for both images
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    # Initialize BFMatcher (Brute-Force Matcher)
    bf = cv2.BFMatcher()

    # Match descriptors of both images
    matches = bf.match(des1, des2)

    # Calculate the difference between the two images based on the matched key points
    diff = sum([match.distance for match in matches])/len(matches)

    return {'SIFT_score': diff}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
