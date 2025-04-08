import argparse
import http.server
import io
import socketserver
import sys

import cv2
import picamera2
from PIL import Image


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


class VideoStreamHandler(http.server.BaseHTTPRequestHandler):
    """
    Custom request handler for serving video stream.
    """

    capture_frame = None

    def do_GET(self):
        """
        Handles GET requests.
        """
        if self.path == "/video_feed":
            self.send_response(200)
            self.send_header(
                "Content-type",
                "multipart/x-mixed-replace; boundary=frame",
            )
            self.end_headers()
            while True:
                # Capture frame-by-frame
                success, frame = VideoStreamHandler.capture_frame()
                if not success:
                    break
                else:
                    img = Image.fromarray(frame)
                    with io.BytesIO() as output:
                        img.save(output, format="JPEG")
                        frame_bytes = output.getvalue()
                    self.wfile.write(b"--frame\r\n")
                    self.send_header(
                        "Content-type",
                        "image/jpeg",
                    )
                    self.send_header(
                        "Content-length",
                        len(frame_bytes),
                    )
                    self.end_headers()
                    self.wfile.write(frame_bytes)
                    self.wfile.write(b"\r\n")
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not found")


def main(host, port):
    """
    Main function to start the server.

    Args:
        host (str): IP address of the server.
        port (int): Port number of the server.
    """
    with socketserver.TCPServer((host, port), VideoStreamHandler) as server:
        print(f"Serving at {host}:{port}\nVideo at {host}:{port}/video_feed")
        server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Camera Server Script")

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

    VideoStreamHandler.capture_frame = get_video_source_fnc(
        args["camera_source_type"],
        int(args["image_width"]),
        int(args["image_height"]),
    )
    main(args["host"], int(args["port"]))
