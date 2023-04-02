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


def validate_input(request_json, required_fields):
    for field, type in required_fields.items():
        # Check that required field is in the request
        if field not in request_json:
            return jsonify({'error': f"Missing property: '{field}'"}), 400
        # Check that type is correct
        if not isinstance(request.json[field], type):
            return jsonify({'error': f"'{field}' is not of type '{type.__name__}'"}), 400
        # If image url, check that the format is correct
        if 'image_url' in field:
            file_ext = request.json[field].split('.')[-1].lower()
            if file_ext not in VALID_IMAGE_FORMATS:
                return jsonify({'error': 'Invalid file format. Only JPG, JPEG and PNG files are allowed.'}), 400
    return None


@app.route('/get_image_hash', methods=['POST'])
def get_image_hash():
    # Validate input
    required_fields = {'image_url': str}
    validation_result = validate_input(request.json, required_fields)
    if validation_result is not None:
        return validation_result

    # Load image, convert to binary and get the hash
    image_url = request.json['image_url']
    try:
        image_data = urllib.request.urlopen(image_url).read()
    except urllib.error.URLError as e:
        return jsonify({'error': f"Failed to fetch image data: {e.reason}"}), 400
    img = Image.open(io.BytesIO(image_data))
    image_hash = hashlib.sha256(img.tobytes()).hexdigest()
    return {'image_hash': image_hash}


@app.route('/center_crop', methods=['POST'])
def center_crop():
    # Validate input
    required_fields = {'image_url': str, 'width': int, 'height': int}
    validation_result = validate_input(request.json, required_fields)
    if validation_result is not None:
        return validation_result

    image_url = request.json['image_url']
    width = request.json['width']
    height = request.json['height']

    # Load image and convert into binary
    try:
        image_data = urllib.request.urlopen(image_url).read()
    except urllib.error.URLError as e:
        return jsonify({'error': f"Failed to fetch image data: {e.reason}"}), 400
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
    # Validate input
    required_fields = {'image_url_1': str, 'image_url_2': str}
    validation_result = validate_input(request.json, required_fields)
    if validation_result is not None:
        return validation_result

    image_url_1 = request.json['image_url_1']
    image_url_2 = request.json['image_url_2']

    # Load images and convert into binary
    try:
        image_data_1 = urllib.request.urlopen(image_url_1).read()
        image_data_2 = urllib.request.urlopen(image_url_2).read()
    except Exception as e:
        return jsonify({'error': f"Failed to fetch image data: {e}"}), 400
    img1 = cv2.imdecode(np.frombuffer(
        image_data_1, np.uint8), cv2.IMREAD_COLOR)
    img2 = cv2.imdecode(np.frombuffer(
        image_data_2, np.uint8), cv2.IMREAD_COLOR)

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
