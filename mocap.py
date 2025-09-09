"""Wrist Motion Capture System

Purpose: To calculate and analyze the angles from color markers.
Allow for user to input ROM ranges with feedback given based on tested ROM.
"""

import numpy as np
import cv2
import math
import datetime
import sys
import csv
import json
import os
from collections import deque
import statistics
import time

# Constants
COLOR_RANGES = {
    'orange': {'low': [9, 110, 30], 'high': [95, 255, 255]},
    'yellow': {'low': [20, 50, 0], 'high': [40, 251, 250]},
    'pink': {'low': [129, 93, 0], 'high': [178, 255, 255]},
    'blue': {'low': [74, 100, 0], 'high': [111, 255, 255]}
}

KERNEL_SIZE = 5
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
CIRCLE_RADIUS = 15
CIRCLE_THICKNESS = 5
LINE_THICKNESS = 8
FONT_SCALE = 3
FONT_THICKNESS = 5
ESC_KEY = 27

# Colors for drawing (BGR format)
COLORS = {
    'orange_circle': (0, 150, 255),
    'yellow_circle': (0, 255, 255),
    'pink_circle': (183, 193, 255),
    'blue_circle': (225, 0, 0),
    'line': (255, 255, 255),
    'text_good': (0, 255, 0),
    'text_bad': (0, 0, 255),
    'text_black': (0, 0, 0)
}


class WristMotionCapture:
    """Main class for wrist motion capture and analysis."""
    
    def __init__(self):
        self.cap = None
        self.kernel = np.ones((KERNEL_SIZE, KERNEL_SIZE), np.uint8)
        self.arm = None
        self.rom_ranges = {}
        
        # Progress tracking
        self.session_start_time = None
        self.session_angles = []
        self.session_feedback = []
        self.radial_angles = []
        self.ulnar_angles = []
        self.total_movements = 0
        self.good_movements = 0
        self.max_radial_achieved = 0
        self.max_ulnar_achieved = 0
        self.recent_angles = deque(maxlen=30)
        
        # Manual recording tracking
        self.recorded_angles = []
        self.recorded_timestamps = []
        self.recorded_movement_types = []
        self.last_recorded_time = 0
        
    def get_user_input(self):
        """Get user configuration input with validation."""
        print("Hello! \nMake sure your wearable is completely fastened.")
        print("Session started - tracking your progress!")
        print("\nControls:")
        print("- ESC: Exit and save session")
        print("- SPACEBAR: Record current angle for tracking")
        print("- R: Reset recorded angles")
        
        # Get arm selection
        while True:
            print("\nType L if the wearable is on your left arm; type R if the wearable is on your right arm:")
            arm = input().upper().strip()
            if arm in ['L', 'R']:
                print("\nThank you")
                self.arm = arm
                break
            else:
                print("Invalid input. Please enter L or R.")
        
        # Get ROM ranges with validation
        try:
            print("Enter your minimum radial deviation (towards thumb) value:")
            min_radial = int(input())
            print("\nEnter your maximum radial deviation (towards thumb) value:")
            max_radial = int(input())
            
            print("\nEnter your minimum ulnar deviation (towards pinky) value:")
            min_ulnar = int(input())
            print("\nEnter your maximum ulnar deviation (towards pinky) value:")
            max_ulnar = int(input())
            
            self.rom_ranges = {
                'min_radial': min_radial,
                'max_radial': max_radial,
                'min_ulnar': min_ulnar,
                'max_ulnar': max_ulnar
            }
            
        except ValueError:
            print("Invalid input. Please enter numeric values for ROM ranges.")
            sys.exit(1)
    
    def initialize_camera(self):
        """Initialize camera capture with error handling."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            sys.exit(1)
        return self.cap
    
    def setup_windows(self):
        """Create display windows."""
        cv2.namedWindow('frame')
        cv2.namedWindow('angles')
        cv2.namedWindow('ROM')
    
    def create_color_masks(self, hsv_img):
        """Create color masks for all marker colors."""
        eroded_hsv = cv2.erode(hsv_img, self.kernel, iterations=1)
        masks = {}
        results = {}
        
        for color, ranges in COLOR_RANGES.items():
            low = np.array(ranges['low'], dtype="uint8")
            high = np.array(ranges['high'], dtype="uint8")
            
            mask = cv2.inRange(eroded_hsv, low, high)
            result = cv2.bitwise_or(hsv_img, hsv_img, mask=mask)
            
            masks[color] = mask
            results[color] = result
        
        return masks, results
    
    def get_centroid(self, image):
        """Calculate centroid of a color-filtered image."""
        eroded = cv2.erode(image, self.kernel, iterations=1)
        grayscale = cv2.cvtColor(eroded, cv2.COLOR_BGR2GRAY)
        moments = cv2.moments(grayscale)
        
        if moments["m00"] == 0:
            return 1, 1  # Default position when marker not detected
        else:
            x = int(moments["m10"] / moments["m00"])
            y = int(moments["m01"] / moments["m00"])
            return x, y
    
    def calculate_angle(self, orange_pos, yellow_pos, pink_pos, blue_pos):
        """Calculate angle between two line segments formed by markers."""
        # Line 1: orange to blue (MG)
        # Line 2: yellow to pink (CY)
        
        gx, gy = blue_pos
        mx, my = orange_pos
        cx, cy = yellow_pos
        yx, yy = pink_pos
        
        # Calculate dot product
        dot_product = ((gx - mx) * (yx - cx)) + ((gy - my) * (yy - cy))
        
        # Calculate magnitudes
        mg_magnitude = math.sqrt((gx - mx)**2 + (gy - my)**2)
        cy_magnitude = math.sqrt((yx - cx)**2 + (yy - cy)**2)
        
        # Calculate denominator
        denominator = mg_magnitude * cy_magnitude
        
        # Avoid division by zero
        if denominator == 0:
            denominator = 0.01
        
        # Calculate angle in radians then convert to degrees
        try:
            angle_rad = math.acos(abs(dot_product) / denominator)
            angle_deg = angle_rad * 180 / math.pi
            final_angle = 180 - angle_deg
            return final_angle
        except ValueError:
            return 0  # Return 0 if calculation fails
    
    def determine_movement_type(self, blue_pos, yellow_pos):
        """Determine if movement is radial or ulnar deviation."""
        blue_x, _ = blue_pos
        yellow_x, _ = yellow_pos
        
        if self.arm == "R":  # Right arm
            if blue_x > yellow_x:
                return "radial"
            else:
                return "ulnar"
        else:  # Left arm
            if blue_x > yellow_x:
                return "ulnar"
            else:
                return "radial"
    
    def get_feedback(self, movement_type, angle):
        """Get feedback message and color based on angle and ROM ranges."""
        if movement_type == "radial":
            min_val = self.rom_ranges['min_radial']
            max_val = self.rom_ranges['max_radial']
        else:
            min_val = self.rom_ranges['min_ulnar']
            max_val = self.rom_ranges['max_ulnar']
        
        if angle > max_val:
            return "TOO FAR", COLORS['text_bad']
        elif angle < min_val:
            return "TOO LITTLE", COLORS['text_bad']
        else:
            return "GREAT", COLORS['text_good']
    
    def save_data(self, angle, movement_type, is_good_movement):
        """Save angle data with progress tracking."""
        try:
            with open("results.csv", "a", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([datetime.datetime.now(), int(angle), movement_type, "GREAT" if is_good_movement else "POOR"])
        except IOError as e:
            print(f"Error saving data: {e}")
        
        # Update session tracking
        self.session_angles.append(angle)
        self.recent_angles.append(angle)
        self.total_movements += 1
        if is_good_movement:
            self.good_movements += 1
        
        if movement_type.lower() == 'radial':
            self.radial_angles.append(angle)
            self.max_radial_achieved = max(self.max_radial_achieved, angle)
        else:
            self.ulnar_angles.append(angle)
            self.max_ulnar_achieved = max(self.max_ulnar_achieved, angle)
    
    def record_manual_angle(self, angle, movement_type):
        """Record angle manually when user presses spacebar."""
        current_time = time.time()
        if current_time - self.last_recorded_time > 0.5:
            self.recorded_angles.append(angle)
            self.recorded_timestamps.append(datetime.datetime.now())
            self.recorded_movement_types.append(movement_type)
            self.last_recorded_time = current_time
            print(f"RECORDED: {angle:.1f}° ({movement_type} deviation)")
            return True
        return False
    
    def reset_recorded_angles(self):
        """Reset all manually recorded angles."""
        self.recorded_angles.clear()
        self.recorded_timestamps.clear()
        self.recorded_movement_types.clear()
        print("Recorded angles reset!")
    
    def save_session_summary(self):
        """Save session summary and recorded angles."""
        # Save recorded angles to separate file
        if len(self.recorded_angles) > 0:
            try:
                with open('recorded_angles.csv', 'a', newline='') as f:
                    writer = csv.writer(f)
                    for i, angle in enumerate(self.recorded_angles):
                        writer.writerow([
                            self.recorded_timestamps[i],
                            angle,
                            self.recorded_movement_types[i],
                            self.arm,
                            'manual_recording'
                        ])
                print(f"Saved {len(self.recorded_angles)} recorded angles to recorded_angles.csv")
            except Exception as e:
                print(f"Error saving recorded angles: {e}")
        
        # Save session summary to JSON
        if self.session_start_time and len(self.session_angles) > 0:
            try:
                history = []
                if os.path.exists('progress_history.json'):
                    with open('progress_history.json', 'r') as f:
                        history = json.load(f)
                
                duration = (datetime.datetime.now() - self.session_start_time).total_seconds() / 60
                accuracy = (self.good_movements / self.total_movements * 100) if self.total_movements > 0 else 0
                avg_angle = statistics.mean(self.session_angles) if self.session_angles else 0
                
                session_summary = {
                    'date': self.session_start_time.isoformat(),
                    'arm': self.arm,
                    'duration_minutes': round(duration, 1),
                    'total_movements': self.total_movements,
                    'accuracy_percentage': round(accuracy, 1),
                    'avg_angle': round(avg_angle, 1),
                    'radial_count': len(self.radial_angles),
                    'ulnar_count': len(self.ulnar_angles),
                    'max_radial': self.max_radial_achieved,
                    'max_ulnar': self.max_ulnar_achieved,
                    'recorded_angles': self.recorded_angles.copy(),
                    'recorded_count': len(self.recorded_angles)
                }
                
                history.append(session_summary)
                
                with open('progress_history.json', 'w') as f:
                    json.dump(history, f, indent=2)
                
                # Print session summary
                print("\n=== SESSION SUMMARY ===")
                print(f"Duration: {session_summary['duration_minutes']} minutes")
                print(f"Total movements: {session_summary['total_movements']}")
                print(f"Accuracy: {session_summary['accuracy_percentage']}%")
                print(f"Average angle: {session_summary['avg_angle']}°")
                print(f"Radial movements: {session_summary['radial_count']} (max: {session_summary['max_radial']}°)")
                print(f"Ulnar movements: {session_summary['ulnar_count']} (max: {session_summary['max_ulnar']}°)")
                if len(self.recorded_angles) > 0:
                    print(f"Manual recordings: {len(self.recorded_angles)} angles saved")
                    print(f"Recorded angles: {[round(a, 1) for a in self.recorded_angles]}")
                print("=======================")
                
            except Exception as e:
                print(f"Error saving session summary: {e}")
    
    def create_feedback_image(self, movement_type, feedback_msg, feedback_color, current_angle):
        """Create the feedback display image with progress tracking."""
        image = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), np.uint8)
        image[:] = [255, 255, 255]  # White background
        
        # Display movement type and current angle
        movement_text = f"{movement_type.title()} Deviation: {current_angle:.1f}°"
        cv2.putText(image, movement_text, (50, 50), cv2.FONT_HERSHEY_PLAIN, 
                   2, COLORS['text_black'], 2, 8)
        
        # Display feedback
        cv2.putText(image, feedback_msg, (50, 150), cv2.FONT_HERSHEY_COMPLEX, 
                   2, feedback_color, 3, 8)
        
        # Display session progress
        accuracy = (self.good_movements / self.total_movements * 100) if self.total_movements > 0 else 0
        cv2.putText(image, f"Session: {self.total_movements} moves, {accuracy:.1f}% accuracy", (20, 200), cv2.FONT_HERSHEY_PLAIN, 1, COLORS['text_black'], 1, 8)
        cv2.putText(image, f"Max Radial: {self.max_radial_achieved:.1f}°", (20, 220), cv2.FONT_HERSHEY_PLAIN, 1, COLORS['text_black'], 1, 8)
        cv2.putText(image, f"Max Ulnar: {self.max_ulnar_achieved:.1f}°", (20, 240), cv2.FONT_HERSHEY_PLAIN, 1, COLORS['text_black'], 1, 8)
        
        # Display recorded angles
        if len(self.recorded_angles) > 0:
            cv2.putText(image, f"Recorded: {len(self.recorded_angles)} angles", (20, 260), cv2.FONT_HERSHEY_PLAIN, 1, COLORS['text_black'], 1, 8)
            last_recorded = self.recorded_angles[-1]
            cv2.putText(image, f"Last: {last_recorded:.1f}°", (20, 280), cv2.FONT_HERSHEY_PLAIN, 1, (0,100,0), 1, 8)
        
        # Display trend
        if len(self.recent_angles) >= 10:
            recent_avg = statistics.mean(list(self.recent_angles)[-10:])
            earlier_avg = statistics.mean(list(self.recent_angles)[:10]) if len(self.recent_angles) >= 20 else recent_avg
            
            if recent_avg > earlier_avg * 1.05:
                trend_text = "Trend: ↗ Improving"
                trend_color = COLORS['text_good']
            elif recent_avg < earlier_avg * 0.95:
                trend_text = "Trend: ↘ Declining"
                trend_color = COLORS['text_bad']
            else:
                trend_text = "Trend: → Stable"
                trend_color = COLORS['text_black']
            
            cv2.putText(image, trend_text, (20, 300), cv2.FONT_HERSHEY_PLAIN, 1, trend_color, 1, 8)
        
        return image
    
    def run(self):
        """Main execution loop."""
        # Setup
        self.get_user_input()
        self.initialize_camera()
        self.setup_windows()
        
        # Initialize session tracking
        self.session_start_time = datetime.datetime.now()
        
        print("Press on video, then ESC to exit...")
        
        while True:
            # Capture frame
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Convert to HSV
            hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create color masks and get results
            masks, results = self.create_color_masks(hsv_img)
            
            # Get centroids for each color
            orange_pos = self.get_centroid(results['orange'])
            yellow_pos = self.get_centroid(results['yellow'])
            pink_pos = self.get_centroid(results['pink'])
            blue_pos = self.get_centroid(results['blue'])
            
            # Draw circles on markers
            cv2.circle(results['orange'], orange_pos, CIRCLE_RADIUS, COLORS['orange_circle'], CIRCLE_THICKNESS)
            cv2.circle(results['yellow'], yellow_pos, CIRCLE_RADIUS, COLORS['yellow_circle'], CIRCLE_THICKNESS)
            cv2.circle(results['pink'], pink_pos, CIRCLE_RADIUS, COLORS['pink_circle'], CIRCLE_THICKNESS)
            cv2.circle(results['blue'], blue_pos, CIRCLE_RADIUS, COLORS['blue_circle'], CIRCLE_THICKNESS)
            
            # Combine all marker images
            combined_image = cv2.bitwise_or(results['orange'], results['yellow'])
            combined_image = cv2.bitwise_or(combined_image, results['pink'])
            combined_image = cv2.bitwise_or(combined_image, results['blue'])
            
            # Draw lines between markers
            cv2.line(combined_image, orange_pos, blue_pos, COLORS['line'], LINE_THICKNESS)
            cv2.line(combined_image, yellow_pos, pink_pos, COLORS['line'], LINE_THICKNESS)
            
            # Calculate angle
            angle = self.calculate_angle(orange_pos, yellow_pos, pink_pos, blue_pos)
            
            # Determine movement type and get feedback
            movement_type = self.determine_movement_type(blue_pos, yellow_pos)
            feedback_msg, feedback_color = self.get_feedback(movement_type, angle)
            
            # Create feedback image with progress info
            feedback_image = self.create_feedback_image(movement_type, feedback_msg, feedback_color, angle)
            
            # Determine if this is a good movement
            is_good_movement = feedback_msg == "GREAT"
            
            # Save data with progress tracking
            self.save_data(angle, movement_type, is_good_movement)
            
            # Display images
            cv2.imshow('ROM', feedback_image)
            cv2.imshow('angles', combined_image)
            cv2.imshow('frame', frame)
            
            # Check for keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            # Manual recording (SPACEBAR = 32)
            if key == 32:  # Spacebar
                self.record_manual_angle(angle, movement_type)
            
            # Reset recorded angles (R key = 114)
            elif key == 114:  # R key
                self.reset_recorded_angles()
            
            # Check for exit
            elif key == ESC_KEY:
                break
        
        # Save session summary before cleanup
        self.save_session_summary()
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()


def main():
    """Main function."""
    try:
        wrist_capture = WristMotionCapture()
        wrist_capture.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()