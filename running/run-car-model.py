import RPi.GPIO as GPIO
import time
import atexit
import cv2
import numpy as np
from tensorflow.keras.models import load_model

class Motor:
    def __init__(self, EnaA, In1A, In2A, EnaB, In1B, In2B):
        self.EnaA = EnaA
        self.In1A = In1A
        self.In2A = In2A
        self.EnaB = EnaB
        self.In1B = In1B
        self.In2B = In2B
        
        # Setup GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.EnaA, GPIO.OUT)
        GPIO.setup(self.In1A, GPIO.OUT)
        GPIO.setup(self.In2A, GPIO.OUT)
        GPIO.setup(self.EnaB, GPIO.OUT)
        GPIO.setup(self.In1B, GPIO.OUT)
        GPIO.setup(self.In2B, GPIO.OUT)
        
        # Initialize PWM
        self.pwmA = GPIO.PWM(self.EnaA, 100)
        self.pwmA.start(0)
        self.pwmB = GPIO.PWM(self.EnaB, 100)
        self.pwmB.start(0)
    
    def move(self, speed=0.2, turn=0, duration=0):
        # Speed and turn adjustments
        speed *= 100
        turn *= 100
        
        # Calculate individual motor speeds based on the speed and turn values
        leftSpeed = max(min(speed - turn, 100), -100)
        rightSpeed = max(min(speed + turn, 100), -100)
        
        # Synchronize the left and right speeds for consistent forward and backward movement
        self.pwmA.ChangeDutyCycle(abs(leftSpeed))
        self.pwmB.ChangeDutyCycle(abs(rightSpeed))
        
        # Control motor direction for left motor
        if leftSpeed > 0:
            GPIO.output(self.In1A, GPIO.HIGH)
            GPIO.output(self.In2A, GPIO.LOW)
        else:
            GPIO.output(self.In1A, GPIO.LOW)
            GPIO.output(self.In2A, GPIO.HIGH)
        
        # Control motor direction for right motor
        if rightSpeed > 0:
            GPIO.output(self.In1B, GPIO.HIGH)
            GPIO.output(self.In2B, GPIO.LOW)
        else:
            GPIO.output(self.In1B, GPIO.LOW)
            GPIO.output(self.In2B, GPIO.HIGH)
        
        time.sleep(duration)
    
    def stop(self):
        self.pwmA.ChangeDutyCycle(0)
        self.pwmB.ChangeDutyCycle(0)
        GPIO.output(self.In1A, GPIO.LOW)
        GPIO.output(self.In2A, GPIO.LOW)
        GPIO.output(self.In1B, GPIO.LOW)
        GPIO.output(self.In2B, GPIO.LOW)

    def cleanup(self):
        self.stop()
        self.pwmA.stop()
        self.pwmB.stop()
        GPIO.cleanup()

class ImageProcessor:
    def __init__(self, model_path):
        self.model = load_model(model_path)
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def warpImg(self, img, points, w, h, inv=False):
        pts1 = np.float32(points)
        pts2 = np.float32([[0,0],[w,0],[0,h],[w,h]])
        if inv:
            matrix = cv2.getPerspectiveTransform(pts2, pts1)
        else:
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarp = cv2.warpPerspective(img, matrix, (w, h))
        return imgWarp
    
    def thresholding(self, img):
        lowerWhite = np.array([160, 0, 0])
        upperWhite = np.array([255, 255, 255])
        maskWhite = cv2.inRange(img, lowerWhite, upperWhite)
        return maskWhite
    
    def capture_image(self):
        ret, frame = self.camera.read()
        
        if not ret:
            raise Exception("Failed to capture image")
        return frame
    
    def preprocess_image(self, img):
        hT, wT, c = img.shape
        points = np.float32([[138, 96], [wT-138, 96], [43, 214], [wT-43, 214]])
        thresholded_img = self.thresholding(img)
        #warped_img = self.warpImg(thresholded_img, points, wT, hT)
        X = np.array(thresholded_img) / 255.0

        if X.ndim == 3:
            X = np.expand_dims(X, axis=-1)

        return X
    
    def predict_turn(self, image):
        preprocessed = self.preprocess_image(image)
        prediction = self.model.predict(preprocessed)
        return prediction[0][0]
    
    def cleanup(self):
        self.camera.release()

# Main control logic
motor = Motor(2, 4, 3, 17, 22, 27)
image_processor = ImageProcessor('model2-3.keras')

def cleanup():
    print("Cleaning up...")
    motor.cleanup()
    image_processor.cleanup()
    print("Cleanup complete.")

atexit.register(cleanup)

try:
    while True:
        # Capture image
        image = image_processor.capture_image()
        
        # Predict turn value
        turn = image_processor.predict_turn(image)
        
        # Set a constant forward speed
        speed = 0.4
        
        # Move the car based on the predicted turn value
        motor.move(speed, turn, 0.1)
                
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Program interrupted by user. Exiting...")
finally:
    cleanup()