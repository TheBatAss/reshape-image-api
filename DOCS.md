# /get_image_hash (POST)

This endpoint accepts an image URL and returns the SHA256 hash of the image as a string.

## Request

- **HTTP Method:** POST
- **Endpoint:** /get_image_hash
- **Content-Type:** application/json

The request body must contain a JSON object with the following properties:

- **image_url:** (string) the URL of the image to hash

## Response

- **Content-Type:** application/json

If successful, the response body will contain a JSON object with a single property:

- **image_hash:** (string) the SHA256 hash of the image

If unsuccessful, the response body will contain a JSON object with a single property:

- **error:** (string) a description of the error that occurred

# /center_crop (POST)

This endpoint accepts an image URL, width, and height, crops the image from the center to the specified dimensions, and returns the cropped image as a JPEG.

## Request

- **HTTP Method:** POST
- **Endpoint:** /center_crop
- **Content-Type:** application/json

The request body must contain a JSON object with the following properties:

- **image_url:** (string) the URL of the image to crop
- **width:** (integer) the width of the desired crop
- **height:** (integer) the height of the desired crop

## Response

- **Content-Type:** image/jpeg

If successful, the response body will contain the JPEG of the cropped image.

If unsuccessful, the response body will contain a JSON object with a single property:

- **error:** (string) a description of the error that occurred

# /get_SIFT_difference (POST)

This endpoint accepts two image URLs, calculates the SIFT score (difference) between the two images, and returns the score as a float. The higher the score the more different the two images are. If identical the score is zero.

Read more: https://en.wikipedia.org/wiki/Scale-invariant_feature_transform

## Request

- **HTTP Method:** POST
- **Endpoint:** /get_SIFT_difference
- **Content-Type:** application/json

The request body must contain a JSON object with the following properties:

- **image_url_1:** (string) the URL of the first image
- **image_url_2:** (string) the URL of the second image

##Response

- **Content-Type:** application/json

If successful, the response body will contain a JSON object with a single property:

- **SIFT_difference:** (float) the SIFT score (difference) between the two images

If unsuccessful, the response body will contain a JSON object with a single property:

- **error:** (string) a description of the error that occurred
