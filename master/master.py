import pandas as pd
import requests
import json
import time
import socket


def send_chunk(worker_url, chunk, timeout_seconds=30):
    """Send one data chunk to a worker and return the parsed JSON response."""
    response = requests.post(
        worker_url,
        json={"data": chunk},
        timeout=timeout_seconds
    )
    if response.status_code != 200:
        raise RuntimeError(f"Worker returned status {response.status_code}")
    return response.json()


def send_chunk_with_failover(preferred_worker_url, all_workers, chunk, timeout_seconds=30):
    """Try the preferred worker first, then fall back to other workers (task reassignment)."""
    ordered_workers = [preferred_worker_url] + [w for w in all_workers if w != preferred_worker_url]
    last_error = None

    for attempt, worker_url in enumerate(ordered_workers, start=1):
        try:
            # Give workers a moment to be ready (especially right after container start)
            time.sleep(2)
            result = send_chunk(worker_url, chunk, timeout_seconds=timeout_seconds)
            return result, worker_url
        except (requests.exceptions.RequestException, RuntimeError) as e:
            last_error = e
            print(f"   WARNING: Attempt {attempt}/{len(ordered_workers)} failed for {worker_url}: {e}")

    raise RuntimeError(f"All workers failed for this chunk. Last error: {last_error}")

def split_data(data, num_workers):
    """
    Split data into chunks for each worker
    
    Args:
        data: list of rows
        num_workers: number of worker nodes
    
    Returns:
        list of chunks
    """
    chunk_size = len(data) // num_workers
    chunks = []
    
    for i in range(num_workers):
        start_idx = i * chunk_size
        if i == num_workers - 1:
            # Last chunk gets remaining rows
            end_idx = len(data)
        else:
            end_idx = start_idx + chunk_size
        
        chunks.append(data[start_idx:end_idx])
    
    return chunks

def main():
    print("=" * 60)
    print("SENTIMENT140 MAPREDUCE - MASTER NODE")
    print("=" * 60)
    
    # Step 1: Load data
    print("\nSTEP 1: Loading data...")
    try:
        df = pd.read_csv("data/mini_data.csv")
        print(f"Loaded {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}")
    except FileNotFoundError:
        print("ERROR: data/mini_data.csv not found!")
        print("   Run: python scripts/create_mini_dataset.py")
        return
    
    # Convert to list
    data = df.values.tolist()
    
    # Step 2: Define workers
    print("\nSTEP 2: Defining workers...")
    workers = [
        "http://worker1:5000/process",
        "http://worker2:5000/process",
        "http://worker3:5000/process"
    ]
    print(f"{len(workers)} workers defined")

    print("Worker IP addresses (Docker network):")
    for worker_url in workers:
        host = worker_url.split("//", 1)[-1].split(":", 1)[0]
        try:
            ip = socket.gethostbyname(host)
        except Exception:
            ip = "unknown"
        print(f"   {host} -> {ip}")
    
    # Step 3: Split data
    print("\nSTEP 3: Splitting data...")
    chunks = split_data(data, len(workers))
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i+1}: {len(chunk)} rows")
    
    # Step 4: Send to workers (MAP phase)
    print("\nSTEP 4: Sending to workers (MAP phase)...")
    results = []

    for i, chunk in enumerate(chunks):
        preferred_worker_url = workers[i % len(workers)]
        print(f"\n   Sending chunk {i+1} ({len(chunk)} rows) to {preferred_worker_url}...")

        try:
            result, used_worker_url = send_chunk_with_failover(
                preferred_worker_url=preferred_worker_url,
                all_workers=workers,
                chunk=chunk,
                timeout_seconds=30
            )
            results.append(result)
            if used_worker_url == preferred_worker_url:
                print(f"   Worker response: {result}")
            else:
                print(f"   Reassigned to {used_worker_url}. Worker response: {result}")
        except Exception as e:
            print(f"   ERROR: {str(e)}")
            print("   Make sure Docker containers are running!")
            return
    
    # Step 5: Aggregate results (REDUCE phase)
    print("\nSTEP 5: Aggregating results (REDUCE phase)...")
    final_result = {
        "positive": 0,
        "negative": 0,
        "total": 0
    }
    
    for result in results:
        final_result["positive"] += result["positive"]
        final_result["negative"] += result["negative"]
        final_result["total"] += result["total"]
    
    # Step 6: Display final results
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Total tweets processed: {final_result['total']}")
    print(f"Positive sentiment: {final_result['positive']} ({final_result['positive']*100/final_result['total']:.1f}%)")
    print(f"Negative sentiment: {final_result['negative']} ({final_result['negative']*100/final_result['total']:.1f}%)")
    print("=" * 60)
    
    # Save results
    with open("results/sentiment_results.json", "w") as f:
        json.dump(final_result, f, indent=2)
    print("Results saved to: results/sentiment_results.json")

if __name__ == "__main__":
    main()
