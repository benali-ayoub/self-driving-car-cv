import pygame
import tkinter as tk
from tkinter import ttk
import threading

class JoystickPreview:
    def __init__(self, root):
        self.root = root
        self.root.title("Joystick Input Preview")
        
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() == 0:
            raise ValueError("No joystick found")
        
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        
        self.create_widgets()
        
        self.running = True
        self.thread = threading.Thread(target=self.update_joystick)
        self.thread.start()
        
    def create_widgets(self):
        # Left Stick
        ttk.Label(self.root, text="Left Stick").grid(row=0, column=0, columnspan=2)
        self.left_x = ttk.Label(self.root, text="X: 0.00")
        self.left_x.grid(row=1, column=0)
        self.left_y = ttk.Label(self.root, text="Y: 0.00")
        self.left_y.grid(row=1, column=1)
        
        # Right Stick
        ttk.Label(self.root, text="Right Stick").grid(row=2, column=0, columnspan=2)
        self.right_x = ttk.Label(self.root, text="X: 0.00")
        self.right_x.grid(row=3, column=0)
        self.right_y = ttk.Label(self.root, text="Y: 0.00")
        self.right_y.grid(row=3, column=1)
        
        # Motor Input Preview
        ttk.Label(self.root, text="Motor Input Preview").grid(row=4, column=0, columnspan=2)
        self.speed = ttk.Label(self.root, text="Speed: 0.00")
        self.speed.grid(row=5, column=0)
        self.turn = ttk.Label(self.root, text="Turn: 0.00")
        self.turn.grid(row=5, column=1)
        
        # Canvas for visual representation
        self.canvas = tk.Canvas(self.root, width=200, height=200, bg="white")
        self.canvas.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
        self.stick_indicator = self.canvas.create_oval(95, 95, 105, 105, fill="red")
        
    def update_joystick(self):
        while self.running:
            pygame.event.pump()
            
            # Check the number of axes for the joystick
            num_axes = self.joystick.get_numaxes()
            
            # Print all axes for debugging
            axes = [round(self.joystick.get_axis(i), 2) for i in range(num_axes)]
            print(f"Axes: {axes}")
            
            # Left stick axes (may vary depending on joystick model)
            left_x = round(self.joystick.get_axis(0), 2)
            left_y = round(self.joystick.get_axis(1), 2)
            
            # Right stick axes - Update these if needed
            right_x = round(self.joystick.get_axis(2), 2)  # This might be axis 2 or 3
            right_y = round(self.joystick.get_axis(3), 2)  # This might be axis 3 or 4
            
            # Calculate motor inputs (using right stick)
            speed = -right_y
            turn = right_x
            
            # Update GUI
            self.root.after(0, self.update_gui, left_x, left_y, right_x, right_y, speed, turn)
            
            pygame.time.wait(50)  # 20 fps update rate

        
    def update_gui(self, left_x, left_y, right_x, right_y, speed, turn):
        self.left_x.config(text=f"X: {left_x}")
        self.left_y.config(text=f"Y: {left_y}")
        self.right_x.config(text=f"X: {right_x}")
        self.right_y.config(text=f"Y: {right_y}")
        self.speed.config(text=f"Speed: {speed:.2f}")
        self.turn.config(text=f"Turn: {turn:.2f}")
        
        # Update stick indicator position
        x = 100 + (right_x * 50)
        y = 100 + (right_y * 50)
        self.canvas.coords(self.stick_indicator, x-5, y-5, x+5, y+5)
        
    def on_closing(self):
        self.running = False
        self.thread.join()
        pygame.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = JoystickPreview(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
