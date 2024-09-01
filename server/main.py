from flask import Flask, Response, request, jsonify
import cv2
from flask_cors import CORS

from image.image_process_main import ImageProcessor

app = Flask(__name__)
CORS(app)

image_processor = ImageProcessor()

def generate_frames():
    camera = cv2.VideoCapture(0)  # Use 0 for the default camera, or the index of the camera

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = image_processor.process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Add a dictionary to store the current state of knobs and values
control_states = {
    "knob1": 0,
    "knob2": 0,
    "value1": 0,
    "value2": 0,
    'YOLO': True,
    'HandLandmark': True
}

def set_control_state(control_name, value):
    control_states[control_name] = value
    if control_name == 'YOLO':
        image_processor.set_yolo(value)
    elif control_name == 'HandLandmark':
        image_processor.set_hand_landmark(value)

@app.route('/set_control/<control_name>', methods=['POST'])
def set_control(control_name):
    if control_name in control_states:
        set_control_state(control_name, request.json.get('value'))
        print(f"{control_name} set to {control_states[control_name]}")
        return jsonify({"status": "success", "control": control_name, "value": control_states[control_name]})
    else:
        return jsonify({"status": "error", "message": "Invalid control name"}), 400

@app.route('/get_control/<control_name>', methods=['GET'])
def get_control(control_name):
    if control_name in control_states:
        return jsonify({"status": "success", "control": control_name, "value": control_states[control_name]})
    else:
        return jsonify({"status": "error", "message": "Invalid control name"}), 400

# Example default route to check server is running
@app.route('/')
def index():
    return "Flask server is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
