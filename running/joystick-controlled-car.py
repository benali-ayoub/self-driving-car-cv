import RPi.GPIO as GPIO
import pygame
from time import sleep

# Motor Control Class
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

# Joystick Control
class JoystickControl:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() == 0:
            raise ValueError("No joystick found")
        
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()
        
        self.buttons = {'x':0,'o':0,'t':0,'s':0,
                   'L1':0,'R1':0,'L2':0,'R2':0,
                   'share':0,'options':0,
                   'axis1':0.,'axis2':0.,'axis3':0.,'axis4':0.}
        self.axiss = [0., 0., 0., 0., 0., 0.]

    def get_js(self, name=''):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                self.axiss[event.axis] = round(event.value, 2)
            elif event.type == pygame.JOYBUTTONDOWN:
                for x, (key, val) in enumerate(self.buttons.items()):
                    if x < 10:
                        if self.controller.get_button(x):
                            self.buttons[key] = 1
            elif event.type == pygame.JOYBUTTONUP:
                for x, (key, val) in enumerate(self.buttons.items()):
                    if x < 10:
                        if event.button == x:
                            self.buttons[key] = 0

        self.buttons['axis1'], self.buttons['axis2'], self.buttons['axis3'], self.buttons['axis4'] = [
            self.axiss[0], self.axiss[1], self.axiss[3], self.axiss[4]
        ]

        if name == '':
            return self.buttons
        else:
            return self.buttons[name]

# Main control logic integrating joystick and motor control
motor = Motor(2, 3, 4, 17, 22, 27)  # Adjust GPIO pins as needed
joystick = JoystickControl()

try:
    while True:
        # Get joystick values
        js = joystick.get_js()
        
        # Map right joystick axes to speed and turn
        speed = -js['axis4']  # Right stick vertical axis for forward/backward
        turn = js['axis3']    # Right stick horizontal axis for left/right
        
        # Apply dead zone to avoid unwanted movement
        if abs(speed) < 0.1:
            speed = 0
        if abs(turn) < 0.1:
            turn = 0
        
        # Move the car based on joystick input
        if speed != 0 or turn != 0:
            motor.move(speed, turn, 0.1)
        else:
            motor.stop()

        sleep(0.05)

except KeyboardInterrupt:
    motor.stop()
    GPIO.cleanup()
    pygame.quit()
