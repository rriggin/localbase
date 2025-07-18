#!/usr/bin/env python3
"""
Analyze call log to find records with call times longer than 90 seconds.
"""

import csv
import re
from datetime import datetime, timedelta

def parse_duration(duration_str):
    """Parse duration string in format 'H:MM:SS' or 'M:SS' to seconds"""
    if not duration_str or duration_str == '-':
        return 0
    
    # Remove any leading/trailing whitespace
    duration_str = duration_str.strip()
    
    # Handle different duration formats
    parts = duration_str.split(':')
    
    if len(parts) == 3:  # H:MM:SS format
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:  # M:SS format
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    else:
        return 0

def analyze_call_duration(csv_file_path, threshold_seconds=90):
    """Analyze call log and find records with duration longer than threshold"""
    
    calls_over_threshold = []
    total_calls = 0
    total_duration = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                total_calls += 1
                
                # Parse duration
                duration_str = row.get('Duration', '')
                duration_seconds = parse_duration(duration_str)
                
                if duration_seconds > 0:
                    total_duration += duration_seconds
                
                # Check if duration is over threshold
                if duration_seconds > threshold_seconds:
                    calls_over_threshold.append({
                        'from': row.get('From', ''),
                        'to': row.get('To', ''),
                        'extension': row.get('Extension', ''),
                        'date': row.get('Date', ''),
                        'time': row.get('Time', ''),
                        'duration': duration_str,
                        'duration_seconds': duration_seconds,
                        'action_result': row.get('Action Result', ''),
                        'direction': row.get('Direction', '')
                    })
    
    except FileNotFoundError:
        print(f"Error: File {csv_file_path} not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Print results
    print(f"Call Log Analysis Results")
    print(f"=" * 50)
    print(f"Total calls analyzed: {total_calls}")
    print(f"Calls longer than {threshold_seconds} seconds: {len(calls_over_threshold)}")
    print(f"Percentage of calls over {threshold_seconds}s: {(len(calls_over_threshold)/total_calls*100):.1f}%")
    
    if total_calls > 0:
        avg_duration = total_duration / total_calls
        print(f"Average call duration: {avg_duration:.1f} seconds ({avg_duration/60:.1f} minutes)")
    
    print(f"\nDetailed list of calls over {threshold_seconds} seconds:")
    print(f"-" * 80)
    
    # Sort by duration (longest first)
    calls_over_threshold.sort(key=lambda x: x['duration_seconds'], reverse=True)
    
    for i, call in enumerate(calls_over_threshold, 1):
        print(f"{i:2d}. {call['duration']} ({call['duration_seconds']}s) - {call['direction']} "
              f"from {call['from']} to {call['to']} - {call['extension']} - {call['date']} {call['time']}")
    
    # Summary statistics
    if calls_over_threshold:
        durations = [call['duration_seconds'] for call in calls_over_threshold]
        max_duration = max(durations)
        min_duration = min(durations)
        avg_long_duration = sum(durations) / len(durations)
        
        print(f"\nStatistics for calls over {threshold_seconds}s:")
        print(f"  Longest call: {max_duration} seconds ({max_duration/60:.1f} minutes)")
        print(f"  Shortest call over threshold: {min_duration} seconds ({min_duration/60:.1f} minutes)")
        print(f"  Average duration of long calls: {avg_long_duration:.1f} seconds ({avg_long_duration/60:.1f} minutes)")

if __name__ == "__main__":
    # Analyze the call log file
    csv_file = "data/CallLog_20250702-153133.csv"
    analyze_call_duration(csv_file, threshold_seconds=90) 