import io#manage input and output operaton file related
import logging#for logging the information 
import socketserver#framework for creating network server, has classes to handle network requests easily
from threading import Thread#use to run multiple threads i.e task at the same time
from threading import Condition#condition is used to notify other thread that they can continue
from http import server# used to  create simple web server locally 
import picamera
from datetime import datetime
import time
import requests


PAGE="""\
<html>
<head>
<title>This is my page-->Niranjan</title>
</head>
<body>
<h1>Niranjan Home Security System</h1>
<img src="http://139.218.225.21:5000/stream1.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream1.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()
#set up stuff for the web server, reuse address true and multiple thread allowed
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def capture_video():
    now = datetime.now().time()
    current_time = now.strftime("%H:%M:%S")
     try:
        camera.start_recording(current_time+'.h264', splitter_port=2)
        camera.wait_recording(10)
     except Exception as e:
                print("An Exception occured:",e)
     finally :
        camera.stop_recording(splitter_port=2)
    
with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    server = StreamingServer(('0.0.0.0', 5000), StreamingHandler)
    server_thread = Thread(target=server.serve_forever)
    output = StreamingOutput()
    camera.rotation=180
    
    camera.start_recording(output, format='mjpeg')
   
    
   
    try:
         server_thread.start()
         while True:
            try:
                x=requests.get('https://api.particle.io/v1/devices/e00fce68753ae072c0393443/motion?access_token=167b5f0c1b5c67677a1a35f1701e7a2fa56b8a66')
                x.raise_for_status()
                data = x.json()
                print(data['result'])
                now = datetime.now().time()
                current_time = now.strftime("%H:%M:%S")
                if (data['result']==True):
                        print("Motion Detected")
                        capture_video()
            except Exception as e:
                print("An Exception occured:",e)
         
            
    finally :
          camera.stop_recording()


