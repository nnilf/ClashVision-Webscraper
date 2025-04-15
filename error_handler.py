import csv
import os
from typing import List

class ErrorHandler:
    def __init__(self, output_file: str = "errors.csv"):
        self.errors: List[str] = []
        self.output_file = output_file
    
    def add_error(self, message: str):
        """Add an error message to be logged"""
        self.errors.append(message)
    
    def save_errors(self):
        """Save all collected error messages to CSV"""
        if not self.errors:
            return
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if os.stat(self.output_file).st_size == 0:  # Write header if empty
                writer.writerow(["Error Messages"])
            writer.writerows([[error] for error in self.errors])
        
        print(f"Saved {len(self.errors)} errors to {self.output_file}")
        self.errors.clear()  # Clear after saving

    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_errors()
        return False  # Don't suppress exceptions