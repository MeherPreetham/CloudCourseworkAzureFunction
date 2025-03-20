import azure.functions as func
import cv2
import numpy as np
import logging
import binascii  # Import the binascii module for hexdump

app = func.FunctionApp()

@app.function_name(name="create_thumbnail")
@app.route(route="create_thumbnail", auth_level=func.AuthLevel.ANONYMOUS)
def create_thumbnail(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function that resizes an image to a thumbnail"""
    try:
        # Get the image data from the request
        image_data = req.get_body()
        if not image_data:
            return func.HttpResponse("No image provided", status_code=400)

        # Log the first 32 bytes of the image data
        logging.info(f"Received image data (first 32 bytes): {binascii.hexlify(image_data[:32])}")

        # Convert byte data to numpy array
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            logging.error("cv2.imdecode failed to decode the image")
            return func.HttpResponse("Invalid image", status_code=400)

        # Log the shape of the image
        logging.info(f"Image shape: {image.shape}")

        # Resize the image to a thumbnail (100x100)
        thumbnail = cv2.resize(image, (100, 100), interpolation=cv2.INTER_AREA)

        # Encode the resized image back to jpg format
        _, encoded_image = cv2.imencode('.jpg', thumbnail) 

        # Log the first 32 bytes of the encoded image
        logging.info(f"Encoded image data (first 32 bytes): {binascii.hexlify(encoded_image[:32])}")

        return func.HttpResponse(encoded_image.tobytes(), mimetype="image/jpg") 

    except Exception as e:
        logging.exception("Error during thumbnail creation:")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
