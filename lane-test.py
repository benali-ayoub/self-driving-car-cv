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
    
    def move(self, speed=0.2, steering_angle=0, duration=0):
        # Calculate motor speed based on steering angle
        leftSpeed = max(min(speed * 100 - steering_angle, 100), -100)
        rightSpeed = max(min(speed * 100 + steering_angle, 100), -100)
        
        # Adjust PWM duty cycles
        self.pwmA.ChangeDutyCycle(abs(leftSpeed))
        self.pwmB.ChangeDutyCycle(abs(rightSpeed))
        
        # Control motor direction for left motor
        GPIO.output(self.In1A, GPIO.HIGH if leftSpeed > 0 else GPIO.LOW)
        GPIO.output(self.In2A, GPIO.LOW if leftSpeed > 0 else GPIO.HIGH)
        
        # Control motor direction for right motor
        GPIO.output(self.In1B, GPIO.HIGH if rightSpeed > 0 else GPIO.LOW)
        GPIO.output(self.In2B, GPIO.LOW if rightSpeed > 0 else GPIO.HIGH)
        
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

class LaneDetector:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def capture_image(self):
        ret, frame = self.camera.read()
        if not ret:
            raise Exception("Failed to capture image")
        return frame

    def detect_lane(self, img):
        # Convert to grayscale and apply Canny edge detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Apply Hough Line Transform to detect lane lines
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=40, maxLineGap=5)
        
        return lines

    def calculate_steering_angle(self, lines, img_width):
        if lines is None:
            return -90  # Default steering angle if no lanes are detected

        # Calculate the midpoint of detected lines to find the lane center
        left_line_x, right_line_x = [], []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1)
            if slope < 0:
                left_line_x.append(x1)
                left_line_x.append(x2)
            else:
                right_line_x.append(x1)
                right_line_x.append(x2)

        # Calculate lane center and vehicle center deviation
        if left_line_x and right_line_x:
            lane_center = (min(left_line_x) + max(right_line_x)) / 2
        elif left_line_x:
            lane_center = max(left_line_x)
        elif right_line_x:
            lane_center = min(right_line_x)
        else:
            return -90  # No lane detected

        vehicle_center = img_width / 2
        deviation = lane_center - vehicle_center

        # Convert deviation to steering angle
        steering_angle = np.arctan(deviation / img_width) * (180 / np.pi)
        return steering_angle
    
    def cleanup(self):
        self.camera.release()

# Main control logic
motor = Motor(2, 4, 3, 17, 22, 27)
lane_detector = LaneDetector()

def cleanup():
    print("Cleaning up...")
    motor.cleanup()
    lane_detector.cleanup()
    print("Cleanup complete.")

atexit.register(cleanup)

try:
    while True:
        # Capture image
        image = lane_detector.capture_image()
        
        # Detect lanes and calculate steering angle
        lines = lane_detector.detect_lane(image)
        img_width = image.shape[1]
        steering_angle = lane_detector.calculate_steering_angle(lines, img_width)
        
        # Set a constant forward speed
        speed = 0.4
        
        # Move the car based on the calculated steering angle
        motor.move(speed, steering_angle, 0.1)
                
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Program interrupted by user. Exiting...")
finally:
    cleanup()
