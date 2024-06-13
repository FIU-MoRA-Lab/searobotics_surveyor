import http.server
import socketserver
import cv2
import picamera2
import sys
import io
import numpy as np
from PIL import Image

def get_video_source_fnc(source='picamera', width=640, height=480):
    """
    Returns a function to read frames from a video source.

    Args:
        source (str): Type of video source. Defaults to 'picamera'.
        width (int): Width of the video frames. Defaults to 640.
        height (int): Height of the video frames. Defaults to 480.

    Returns:
        function: A function to read frames from the specified video source.
    """

    if source == 'picamera':
        try:
            video_capture = picamera2.Picamera2()
            camera_config = video_capture.create_preview_configuration(
                main={'size' : (width, height), # Set preview resolution
                      'format' : "BGR888"})   # For some random reason it maps to RGB
            video_capture.configure(camera_config)
            video_capture.start()
            print('PiCamera found')

            def read_frame():
                return True, video_capture.capture_array()
            return read_frame

        except Exception as e:
            print(f'PiCamera not found: {e}')
            sys.exit(1)
            
    elif source == 'usb':
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
        if self.path == '/video_feed':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                # Capture frame-by-frame
                success, frame = VideoStreamHandler.capture_frame()
                if not success:
                    break
                else:
                    img = Image.fromarray(frame)
                    with io.BytesIO() as output:
                        img.save(output, format='JPEG')
                        frame_bytes = output.getvalue()
                    self.wfile.write(b'--frame\r\n')
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(frame_bytes))
                    self.end_headers()
                    self.wfile.write(frame_bytes)
                    self.wfile.write(b'\r\n')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')


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
    """
    Server broadcasting picamera image to a given ip address

    Args:
        host (str): IP address of the server.
        port (int): Port number of the server.
        camera_source_type (str): Type of camera source (e.g., 'usb').
        image_width (int): Width of the image frame.
        image_height (int): Height of the image frame.
    """
    args = {'host': '192.168.0.20',
            'port': 5001,
            'camera_source_type': 'picamera',
            'image_width': 800,
            'image_height': 600}

    if (len(sys.argv) == 2) or (len(sys.argv) > len(args) + 1):
        print("Usage: python picamera_server.py <host_ip> <port> <camera_source_type> <image_width> <image_height>. If providing arguments, provide at least the first two. ")
        sys.exit(1)
    elif len(sys.argv) > 1:
        args.update(zip(args.keys(), sys.argv[1:]))
        
    VideoStreamHandler.capture_frame = get_video_source_fnc(args['camera_source_type'], int(args['image_width']), int(args['image_height']))
    main(args['host'], int(args['port']))

