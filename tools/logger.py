import csv
import os
from datetime import datetime

def log_signal(signal_data, filename="trade_history.csv"):
    """
    Appends a signal result to a CSV file.
    signal_data: A dictionary containing 'Ticker', 'Signal', 'RSI', etc.
    """
    file_exists = os.path.isfile(filename)
    
    # Add timestamp to the log entry
    signal_data['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Define the headers
    headers = ['Timestamp', 'Ticker', 'Signal', 'RSI']
    
    with open(filename, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        
        # Write header only if the file is new
        if not file_exists:
            writer.writeheader()
            
        writer.writerow(signal_data)
        
    print(f"Logged: {signal_data['Ticker']} - {signal_data['Signal']} at {signal_data['Timestamp']}")