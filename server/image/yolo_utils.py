from ultralytics import YOLO

class YoloProcesser:
    def __init__(self):
        self.model = YOLO('yolov8n')
        self.prev_result = None

    def get_results(self, frame):
        results = self.model([frame])
        return results

    def process_frame_yolo(self, frame, img = None, do_prediction = True, enable=True):
        if not enable:
            if img is None:
                img = frame
            return img, None
        if do_prediction or self.prev_result is None:
            result = self.get_results(frame)[0]
            self.prev_result = result
        else:
            result = self.prev_result
        return result.plot(img = img), result

    def print_results(self, results):
        # Process results list
        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            masks = result.masks  # Masks object for segmentation masks outputs
            keypoints = result.keypoints  # Keypoints object for pose outputs
            probs = result.probs  # Probs object for classification outputs
            obb = result.obb  # Oriented boxes object for OBB outputs
            
            print(boxes)
            result.show()  # display to screen
            result.save(filename="result.jpg")  # save to disk

