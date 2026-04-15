#!/usr/bin/env python3
"""
CREATE MINI DATASET
Samples 300,000 rows from Sentiment140 for Docker testing
"""

import pandas as pd
import os

print("\n" + "="*70)
print("MINI DATASET CREATION SCRIPT")
print("="*70)

# YOUR FILE PATH - CHANGE THIS
file_path = r"C:\Datasets\training.1600000.processed.noemoticon.csv"

print(f"\nDataset path: {file_path}")
print("Loading dataset (30-60 seconds)...")

try:
    # Load with latin-1 encoding (Sentiment140 standard)
    df = pd.read_csv(file_path, encoding="latin-1", header=None)
    print(f"Loaded: {len(df):,} rows")
    
except FileNotFoundError:
    print(f"ERROR: File not found at: {file_path}")
    print("   Please check the path is correct!")
    exit(1)

# Show original columns
print(f"Original columns: {list(range(len(df.columns)))}")
print("   Col 0: Sentiment")
print("   Col 5: Text")

# Keep only needed columns
print("\nExtracting columns 0 (sentiment) and 5 (text)...")
df = df[[0, 5]]
df.columns = ["sentiment", "text"]

# Convert sentiment labels
print("Converting sentiment labels: 4→1 (positive), 0→0 (negative)...")
df["sentiment"] = df["sentiment"].replace(4, 1)

print(f"   Unique values: {sorted(df['sentiment'].unique())}")

# Sample 300,000 rows
print("\nSampling 300,000 rows...")
mini = df.sample(n=300000, random_state=42)

# Create directory if needed
os.makedirs("master/data", exist_ok=True)

# Save
output_path = "master/data/mini_data.csv"
mini.to_csv(output_path, index=False)

print(f"SUCCESS! Saved to: {output_path}")
print("\nDataset Info:")
print(f"   Total rows: {len(mini)}")
print(f"   Positive: {(mini['sentiment']==1).sum()} ({(mini['sentiment']==1).sum()/len(mini)*100:.1f}%)")
print(f"   Negative: {(mini['sentiment']==0).sum()} ({(mini['sentiment']==0).sum()/len(mini)*100:.1f}%)")

print("\nFirst 3 rows:")
print(mini.head(3))

print("\n" + "="*70)
print("Ready to run Docker! Execute: docker-compose up --build")
print("="*70 + "\n")
