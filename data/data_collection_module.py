import cv2
import csv
import os
from datetime import datetime

class DataCollector:
    def __init__(self, image_folder='collected_data/images', csv_file='collected_data/steering_data.csv'):
        self.image_folder = image_folder
        self.csv_file = csv_file
        
        # Create folders if they don't exist
        os.makedirs(self.image_folder, exist_ok=True)
        os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
        
        # Initialize camera
        self.camera = cv2.VideoCapture(0)  # Use 0 for the default camera
        
        # Initialize CSV file
        with open(self.csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Image_Filename', 'Steering_Angle'])
    
    def capture_frame(self, steering_angle):
        ret, frame = self.camera.read()
        if ret:
            # Generate unique filename based on timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            image_filename = f"{timestamp}.jpg"
            image_path = os.path.join(self.image_folder, image_filename)
            
            # Save image
            cv2.imwrite(image_path, frame)
            
            # Write data to CSV
            with open(self.csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, image_filename, steering_angle])
            
            return True
        return False
    
    def close(self):
        self.camera.release()

# Example usage
if __name__ == "__main__":
    collector = DataCollector()
    
    # Simulate capturing 10 frames with random steering angles
    import random
    for _ in range(10):
        angle = random.uniform(-1, 1)  # Random angle between -1 and 1
        collector.capture_frame(angle)
    
    collector.close()
    print("Data collection complete.")
