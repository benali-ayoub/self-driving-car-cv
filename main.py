import RPi.GPIO as GPIO
from time import sleep
import pygame

# Motor Control Class
class Motor:
    def _init_(self, EnaA, In1A, In2A, EnaB, In1B, In2B):
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
    
    def move(self, speed=0.5, turn=0, duration=0):
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
        elif leftSpeed < 0:
            GPIO.output(self.In1A, GPIO.LOW)
            GPIO.output(self.In2A, GPIO.HIGH)
        else:
            GPIO.output(self.In1A, GPIO.LOW)
            GPIO.output(self.In2A, GPIO.LOW)
        
        # Control motor direction for right motor
        if rightSpeed > 0:
            GPIO.output(self.In1B, GPIO.HIGH)
            GPIO.output(self.In2B, GPIO.LOW)
        elif rightSpeed < 0:
            GPIO.output(self.In1B, GPIO.LOW)
            GPIO.output(self.In2B, GPIO.HIGH)
        else:
            GPIO.output(self.In1B, GPIO.LOW)
            GPIO.output(self.In2B, GPIO.LOW)
        
        sleep(duration)
    
    def stop(self, duration=0):
        self.pwmA.ChangeDutyCycle(0)
        self.pwmB.ChangeDutyCycle(0)
        GPIO.output(self.In1A, GPIO.LOW)
        GPIO.output(self.In2A, GPIO.LOW)
        GPIO.output(self.In1B, GPIO.LOW)
        GPIO.output(self.In2B, GPIO.LOW)
        sleep(duration)

# Keyboard Control
class KeyboardControl:
    def _init_(self):
        pygame.init()
        pygame.display.set_mode((100, 100))  # Create a small window

    def get_key(self, key_name):
        for event in pygame.event.get():
            pass
        key_input = pygame.key.get_pressed()
        my_key = getattr(pygame, f'K_{key_name}')
        return key_input[my_key]

# Main control logic integrating keyboard and motor control
motor = Motor(2, 3, 4, 17, 22, 27)  # Adjust GPIO pins as needed
keyboard = KeyboardControl()

try:
    while True:
        speed = 0
        turn = 0

        # Forward and backward control
        if keyboard.get_key('UP'):
            speed = 0.6  # Forward
        elif keyboard.get_key('DOWN'):
            speed = -0.6  # Backward
        
        # Turning control
        if keyboard.get_key('LEFT'):
            turn = -0.6  # Increase this value for tighter left turns
        elif keyboard.get_key('RIGHT'):
            turn = 0.6   # Increase this value for tighter right turns

        # Ensure the motors are always synchronized
        if speed != 0:
            motor.move(speed, turn, 0.1)
        else:
            motor.stop()

        sleep(0.05)

except KeyboardInterrupt:
    motor.stop()
    GPIO.cleanup()