#!/usr/bin/env python3
"""
Analyze Aya Call Log CSV to find records with call times longer than 90 seconds.
"""

import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List

def analyze_aya_call_duration(csv_file_path: str, threshold_seconds: int = 90):
    """Analyze Aya call log and find records with duration longer than threshold"""
    
    calls_over_threshold = []
    total_calls = 0
    total_duration = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                total_calls += 1
                
                # Parse duration from "Call Length" column
                duration_str = row.get('Call Length', '')
                try:
                    duration_seconds = int(duration_str) if duration_str else 0
                except ValueError:
                    duration_seconds = 0
                
                if duration_seconds > 0:
                    total_duration += duration_seconds
                
                # Check if duration is over threshold
                if duration_seconds > threshold_seconds:
                    calls_over_threshold.append({
                        'from_name': row.get('From Name', ''),
                        'to_name': row.get('To Name', ''),
                        'result': row.get('Result', ''),
                        'duration': duration_seconds,
                        'duration_formatted': format_duration(duration_seconds),
                        'call_start_time': row.get('Call Start Time', ''),
                        'call_direction': row.get('Call Direction', ''),
                        'queue': row.get('Queue', '')
                    })
    
    except FileNotFoundError:
        print(f"Error: File {csv_file_path} not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Print results
    print(f"Aya Call Log Analysis Results")
    print(f"=" * 50)
    print(f"Total calls analyzed: {total_calls}")
    print(f"Calls longer than {threshold_seconds} seconds: {len(calls_over_threshold)}")
    print(f"Percentage of calls over {threshold_seconds}s: {(len(calls_over_threshold)/total_calls*100):.1f}%")
    
    if total_calls > 0:
        avg_duration = total_duration / total_calls
        print(f"Average call duration: {avg_duration:.1f} seconds ({avg_duration/60:.1f} minutes)")
    
    print(f"\nDetailed list of calls over {threshold_seconds} seconds:")
    print(f"-" * 100)
    
    # Sort by duration (longest first)
    calls_over_threshold.sort(key=lambda x: x['duration'], reverse=True)
    
    for i, call in enumerate(calls_over_threshold, 1):
        print(f"{i:2d}. {call['duration_formatted']} ({call['duration']}s) - {call['call_direction']} "
              f"to {call['to_name']} - {call['result']} - {call['call_start_time']}")
    
    # Summary statistics
    if calls_over_threshold:
        durations = [call['duration'] for call in calls_over_threshold]
        max_duration = max(durations)
        min_duration = min(durations)
        avg_long_duration = sum(durations) / len(durations)
        
        print(f"\nStatistics for calls over {threshold_seconds}s:")
        print(f"  Longest call: {max_duration} seconds ({max_duration/60:.1f} minutes)")
        print(f"  Shortest call over threshold: {min_duration} seconds ({min_duration/60:.1f} minutes)")
        print(f"  Average duration of long calls: {avg_long_duration:.1f} seconds ({avg_long_duration/60:.1f} minutes)")
        
        # Additional analysis
        print(f"\nCall Direction Analysis:")
        direction_counts = {}
        for call in calls_over_threshold:
            direction = call['call_direction']
            direction_counts[direction] = direction_counts.get(direction, 0) + 1
        
        for direction, count in direction_counts.items():
            print(f"  {direction}: {count} calls")
        
        # Result analysis
        print(f"\nCall Result Analysis:")
        result_counts = {}
        for call in calls_over_threshold:
            result = call['result']
            result_counts[result] = result_counts.get(result, 0) + 1
        
        for result, count in result_counts.items():
            print(f"  {result}: {count} calls")

def format_duration(seconds: int) -> str:
    """Format duration in seconds to MM:SS or HH:MM:SS format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def analyze_call_patterns(csv_file_path: str):
    """Analyze call patterns and trends"""
    try:
        df = pd.read_csv(csv_file_path)
        
        print(f"\nCall Pattern Analysis")
        print(f"=" * 50)
        
        # Convert Call Start Time to datetime
        df['Call Start Time'] = pd.to_datetime(df['Call Start Time'], errors='coerce')
        
        # Add date and hour columns
        df['Date'] = df['Call Start Time'].dt.date
        df['Hour'] = df['Call Start Time'].dt.hour
        
        # Call volume by date
        print(f"Call Volume by Date:")
        date_counts = df['Date'].value_counts().sort_index()
        for date, count in date_counts.items():
            print(f"  {date}: {count} calls")
        
        # Call volume by hour
        print(f"\nCall Volume by Hour:")
        hour_counts = df['Hour'].value_counts().sort_index()
        for hour, count in hour_counts.items():
            print(f"  {hour:02d}:00: {count} calls")
        
        # Average call duration by day
        print(f"\nAverage Call Duration by Date:")
        daily_avg = df.groupby('Date')['Call Length'].mean().sort_index()
        for date, avg_duration in daily_avg.items():
            print(f"  {date}: {avg_duration:.1f} seconds ({avg_duration/60:.1f} minutes)")
        
    except Exception as e:
        print(f"Error in pattern analysis: {e}")

def analyze_working_days(csv_file_path: str, min_calls_threshold: int = 10):
    """Analyze average calls per working day by filtering out low-volume days"""
    try:
        df = pd.read_csv(csv_file_path)
        
        # Convert Call Start Time to datetime
        df['Call Start Time'] = pd.to_datetime(df['Call Start Time'], errors='coerce')
        
        # Add date column
        df['Date'] = df['Call Start Time'].dt.date
        
        # Count calls per date
        date_counts = df['Date'].value_counts().sort_index()
        
        # Filter for working days (days with minimum call threshold)
        working_days = date_counts[date_counts >= min_calls_threshold]
        non_working_days = date_counts[date_counts < min_calls_threshold]
        
        print(f"\nWorking Days Analysis (minimum {min_calls_threshold} calls per day)")
        print(f"=" * 60)
        
        print(f"Working Days ({len(working_days)} days):")
        total_working_calls = 0
        for date, count in working_days.items():
            print(f"  {date}: {count} calls")
            total_working_calls += count
        
        print(f"\nNon-Working Days ({len(non_working_days)} days):")
        for date, count in non_working_days.items():
            print(f"  {date}: {count} calls")
        
        # Calculate averages
        if len(working_days) > 0:
            avg_calls_per_working_day = total_working_calls / len(working_days)
            print(f"\nSummary:")
            print(f"  Total working days: {len(working_days)}")
            print(f"  Total calls on working days: {total_working_calls}")
            print(f"  Average calls per working day: {avg_calls_per_working_day:.1f}")
            print(f"  Total non-working days: {len(non_working_days)}")
            print(f"  Total calls on non-working days: {non_working_days.sum()}")
        
        return working_days, non_working_days
        
    except Exception as e:
        print(f"Error in working days analysis: {e}")
        return None, None

def calculate_connect_rate(csv_file_path: str, threshold_seconds: int = 90):
    """Calculate connect rate based on calls longer than threshold (meaningful interactions)"""
    try:
        df = pd.read_csv(csv_file_path)
        
        total_calls = len(df)
        meaningful_calls = len(df[df['Call Length'] >= threshold_seconds])
        
        connect_rate = (meaningful_calls / total_calls * 100) if total_calls > 0 else 0
        
        print(f"\nConnect Rate Analysis (calls ≥ {threshold_seconds} seconds)")
        print(f"=" * 60)
        print(f"Total calls: {total_calls}")
        print(f"Meaningful calls (≥{threshold_seconds}s): {meaningful_calls}")
        print(f"Connect rate: {connect_rate:.1f}%")
        
        # Break down by call result
        print(f"\nConnect Rate by Call Result:")
        result_breakdown = df.groupby('Result').agg({
            'Call Length': ['count', lambda x: (x >= threshold_seconds).sum()]
        }).round(2)
        
        for result in df['Result'].unique():
            result_calls = df[df['Result'] == result]
            total_result_calls = len(result_calls)
            meaningful_result_calls = len(result_calls[result_calls['Call Length'] >= threshold_seconds])
            result_connect_rate = (meaningful_result_calls / total_result_calls * 100) if total_result_calls > 0 else 0
            
            print(f"  {result}: {meaningful_result_calls}/{total_result_calls} calls ({result_connect_rate:.1f}%)")
        
        # Connect rate by day
        print(f"\nConnect Rate by Date:")
        df['Call Start Time'] = pd.to_datetime(df['Call Start Time'], errors='coerce')
        df['Date'] = df['Call Start Time'].dt.date
        
        daily_stats = []
        for date in df['Date'].unique():
            day_calls = df[df['Date'] == date]
            total_day_calls = len(day_calls)
            meaningful_day_calls = len(day_calls[day_calls['Call Length'] >= threshold_seconds])
            day_connect_rate = (meaningful_day_calls / total_day_calls * 100) if total_day_calls > 0 else 0
            
            daily_stats.append({
                'date': date,
                'total_calls': total_day_calls,
                'meaningful_calls': meaningful_day_calls,
                'connect_rate': day_connect_rate
            })
        
        # Sort by date and show only working days (10+ calls)
        daily_stats.sort(key=lambda x: x['date'])
        working_day_stats = [stat for stat in daily_stats if stat['total_calls'] >= 10]
        
        for stat in working_day_stats:
            print(f"  {stat['date']}: {stat['meaningful_calls']}/{stat['total_calls']} calls ({stat['connect_rate']:.1f}%)")
        
        # Average connect rate for working days
        if working_day_stats:
            avg_working_connect_rate = sum(stat['connect_rate'] for stat in working_day_stats) / len(working_day_stats)
            print(f"\nAverage connect rate on working days: {avg_working_connect_rate:.1f}%")
        
        return connect_rate, meaningful_calls, total_calls
        
    except Exception as e:
        print(f"Error in connect rate analysis: {e}")
        return 0, 0, 0

def create_call_outcome_pie_chart(csv_file_path: str):
    """Create a pie chart showing Aya's calls by outcome/result"""
    try:
        df = pd.read_csv(csv_file_path)
        
        # Count calls by result
        outcome_counts = df['Result'].value_counts()
        
        # Create the pie chart
        plt.figure(figsize=(10, 8))
        
        # Define colors for different outcomes
        colors = ['#2E8B57', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        # Create pie chart
        wedges, texts, autotexts = plt.pie(
            outcome_counts.values, 
            labels=outcome_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors[:len(outcome_counts)],
            textprops={'fontsize': 12}
        )
        
        # Enhance the text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.title('Aya\'s Call Outcomes', fontsize=16, fontweight='bold', pad=20)
        
        # Add total calls count as subtitle
        total_calls = len(df)
        plt.figtext(0.5, 0.02, f'Total Calls: {total_calls}', 
                   ha='center', fontsize=12, style='italic')
        
        # Add legend with call counts
        legend_labels = [f'{outcome} ({count} calls)' for outcome, count in outcome_counts.items()]
        plt.legend(wedges, legend_labels, title="Call Outcomes", 
                  loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Save the chart
        plt.tight_layout()
        plt.savefig('data/aya_call_outcomes_pie_chart.png', dpi=300, bbox_inches='tight')
        print(f"\nPie chart saved as: data/aya_call_outcomes_pie_chart.png")
        
        # Show the chart
        plt.show()
        
        # Print summary statistics
        print(f"\nCall Outcomes Summary:")
        print(f"=" * 40)
        for outcome, count in outcome_counts.items():
            percentage = (count / total_calls) * 100
            print(f"{outcome}: {count} calls ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"Error creating pie chart: {e}")

def main():
    """Main function to analyze Aya call log"""
    csv_file = "data/Aya-Call-Log.csv"
    
    # Analyze call durations
    analyze_aya_call_duration(csv_file, threshold_seconds=90)
    
    # Calculate connect rate (calls ≥ 90 seconds)
    calculate_connect_rate(csv_file, threshold_seconds=90)
    
    # Create pie chart of call outcomes
    create_call_outcome_pie_chart(csv_file)
    
    # Analyze call patterns
    analyze_call_patterns(csv_file)
    
    # Analyze working days
    analyze_working_days(csv_file, min_calls_threshold=10)

if __name__ == "__main__":
    main() 