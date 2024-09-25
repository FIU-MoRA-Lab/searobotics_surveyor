from flask import Flask, Response
from PIL import Image
import cv2
import io
import sys
import picamera2

app = Flask(__name__)

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



def generate_frames():
    global video_capture_src
    """
    Generates video frames from the webcam feed.

    Yields:
        bytes: JPEG-encoded image frames in byte format.
    """

    while True:
        # Capture frame-by-frame
        success, frame = video_capture_src()

        if not success:
            break

        image = Image.fromarray(frame)
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format='JPEG')
        imgByteArr = imgByteArr.getvalue()
        print('Sending image...')
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + imgByteArr + b'\r\n')

@app.route('/')
def index():
    """
    Displays a message indicating that the stream is online.
    """
    return 'Stream online!'

@app.route('/video_feed')
def video_feed():
    """
    Route for accessing the video feed.

    Returns:
        Response: Response object containing the video frames in multipart/x-mixed-replace format.
    """
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def main(host, port):
    app.run(debug=False, host=args['host'], port=args['port'])

if __name__ == '__main__':
    """
    Flask server broadcasting picamera image to a given ip address

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
    
    if len(sys.argv) > 1:
        args.update(zip(args.keys(), sys.argv[1:]))
        
    video_capture_src = get_video_source_fnc(args['camera_source_type'], args['image_width'], args['image_height'])
    main(args['host'], args['port'])
