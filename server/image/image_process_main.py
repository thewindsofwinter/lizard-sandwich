from image.hand_landmark_utils import HandLandmarkerProcessor
from image.hand_gesture_utils import HandGestureProcessor
from image.yolo_utils import YoloProcesser

class ImageProcessor:
    def __init__(self):
        self.frame_process_cnt = 0
        self.hand_gesture_processor = HandGestureProcessor()
        self.yolo_processor = YoloProcesser()
        self.enable_yolo = True
        self.enable_hand_landmark = True

    def process_frame(self, frame):
        do_yolo = self.frame_process_cnt % 6 == 0 
        do_hl = self.frame_process_cnt % 2 == 0 
        self.frame_process_cnt += 1
        
        # Convert the BGR image to RGB before processing.
        hl_frame, hl_res = self.hand_gesture_processor.process_frame_hand_gesture(frame, do_prediction=do_hl, enable = self.enable_hand_landmark)
        yolov8_frame, yolo_res = self.yolo_processor.process_frame_yolo(frame, img = hl_frame, do_prediction = do_yolo, enable = self.enable_yolo)

        return yolov8_frame
    
    def set_yolo(self, enable):
        self.enable_yolo = enable
        
    def set_hand_landmark(self, enable):
        self.enable_hand_landmark = enable
    