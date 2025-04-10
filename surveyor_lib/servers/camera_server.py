import argparse
import io
import sys

import cv2
import picamera2
from flask import Flask, Response
from PIL import Image

app = Flask(__name__)


def get_video_source_fnc(source="picamera", width=640, height=480):
    """
    Returns a function to read frames from a video source.

    Args:
        source (str): Type of video source. Defaults to 'picamera'.
        width (int): Width of the video frames. Defaults to 640.
        height (int): Height of the video frames. Defaults to 480.

    Returns:
        function: A function to read frames from the specified video source.
    """

    if source == "picamera":
        try:
            video_capture = picamera2.Picamera2()
            camera_config = video_capture.create_preview_configuration(
                main={
                    "size": (
                        width,
                        height,
                    ),  # Set preview resolution
                    "format": "BGR888",
                }
            )  # For some random reason it maps to RGB
            video_capture.configure(camera_config)
            video_capture.start()
            print("PiCamera found")

            def read_frame():
                return (
                    True,
                    video_capture.capture_array(),
                )

            return read_frame

        except Exception as e:
            print(f"PiCamera not found: {e}")
            sys.exit(1)

    elif source == "usb":
        # Iterate through possible indices to find an available webcam
        for i in range(10):
            video_capture = cv2.VideoCapture(i)
            if video_capture.isOpened():
                print(f"Webcam found at index {i}")

            # Set webcam resolution
            video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            # Define a function to read frames from the webcam
            def read_frame():
                success, frame = video_capture.read()
                return success, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            return read_frame

        print("No webcam found")
        sys.exit(1)
    else:
        print(f"Unsupported video source: {source}")
        sys.exit(1)


def generate_frames():
    """
    Generates video frames from the webcam feed.

    Yields:
        bytes: JPEG-encoded image frames in byte format.
    """

    while True:
        # Capture frame-by-frame
        success, frame = video_capture_src()

        if success:
            print("Sending image...", end="\r")
        else:
            print("Image not found, closing video capture...")
            break

        image = Image.fromarray(frame)
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format="JPEG")
        imgByteArr = imgByteArr.getvalue()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + imgByteArr + b"\r\n"
        )


@app.route("/")
def index():
    """
    Displays a message indicating that the stream is online.
    """
    return "Camera stream online!"


@app.route("/video_feed")
def video_feed():
    """
    Route for accessing the video feed.

    Returns:
        Response: Response object containing the video frames in multipart/x-mixed-replace format.
    """
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def main(host, port):
    app.run(debug=False, host=host, port=port)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Camera Server Script using Flask"
    )

    # Add arguments with default values
    parser.add_argument(
        "--host",
        type=str,
        default="192.168.0.20",
        help="Host IP (default: 192.168.0.20).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5001,
        help="Port number (default: 5001).",
    )
    parser.add_argument(
        "--camera_source_type",
        type=str,
        default="picamera",
        help="Camera source type (default: picamera).",
    )
    parser.add_argument(
        "--image_width",
        type=int,
        default=800,
        help="Image width (default: 800).",
    )
    parser.add_argument(
        "--image_height",
        type=int,
        default=600,
        help="Image height (default: 600).",
    )

    # Parse the command line arguments
    args = vars(parser.parse_args())

    video_capture_src = get_video_source_fnc(
        args["camera_source_type"],
        args["image_width"],
        args["image_height"],
    )
    main(args["host"], args["port"])
