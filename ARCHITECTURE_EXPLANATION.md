# SYSTEM ARCHITECTURE EXPLANATION

## HIGH-LEVEL OVERVIEW

```
DATA SOURCE (Sentiment140)
  ↓ (300,000 tweets sampled)
  ↓
┌──────────────────────────────────────┐
│         MASTER NODE                   │
│  (Docker Container - sentiment_master)│
│                                       │
│  Tasks:                               │
│  • Load 300,000 tweets from CSV       │
│  • Split data into 3 chunks           │
│  • Send chunks to workers             │
│  • Aggregate results                  │
│  • Calculate final sentiment counts   │
└──────────────────────────────────────┘
      ↓           ↓           ↓
    ┌───────┐   ┌───────┐   ┌───────┐
    │ Worker │   │ Worker │   │ Worker │
    │   #1   │   │   #2   │   │   #3   │
    │  5001  │   │  5002  │   │  5003  │
    └───────┘   └───────┘   └───────┘
      ↓           ↓           ↓
     Process     Process     Process
     100000      100000      100000
     tweets      tweets      tweets
      ↓           ↓           ↓
     Return      Return      Return
     pos/neg     pos/neg     pos/neg
      └─────────┬─────────┘
            ↓
       FINAL AGGREGATION
        Total: 300,000
```

---

## SYSTEM COMPONENTS

### 1. MASTER NODE (`master/master.py`)

**Role:** Orchestrator / Brain of the system

**Responsibilities:**
- Load sentiment140 data from CSV (mini_data.csv)
- Split data into 3 chunks (about 100,000 rows each for a 300,000-row sample)
- Send data chunks to workers via HTTP POST requests
- Collect results from workers
- Aggregate (sum) the sentiment counts
- Display final statistics

**Key Code:**
```python
# Load data
df = pd.read_csv("data/mini_data.csv")

# Split data
chunks = split_data(data, num_workers=3)

# Send to workers
response = requests.post("http://worker1:5000/process", json={"data": chunks[0]})

# Aggregate
final_result["positive"] += response.json()["positive"]
```

**Communication:**
- Receives HTTP responses from workers
- Port: 5000 (internal), exposed as 5000 (external)

---

### 2. WORKER NODES (`worker/worker.py`)

**Role:** Data Processors / Executors

**Responsibilities:**
- Receive data chunk from master
- Count positive tweets (sentiment=1)
- Count negative tweets (sentiment=0)
- Return counts to master

**Deployment:**
- Worker #1: Container port 5000, exposed as 5001
- Worker #2: Container port 5000, exposed as 5002
- Worker #3: Container port 5000, exposed as 5003
- All accessible via Docker internal network

**Key Code:**
```python
@app.route('/process', methods=['POST'])
def process():
    data = request.json['data']  # Receive chunk
    for row in data:
        if row[0] == 1:  # Positive
            positive_count += 1
    return jsonify({"positive": positive_count, "negative": negative_count})
```

---

## MAPREDUCE WORKFLOW

### Phase 1: SPLIT (Master)
```
300,000 tweets
     ↓
  ──────  → Worker 1 gets rows 0-100000
  ──────  → Worker 2 gets rows 100000-200000
  ──────  → Worker 3 gets rows 200000-300000
```

### Phase 2: MAP (Workers)
```
Worker 1: Count pos/neg → {pos:50000, neg:50000}
Worker 2: Count pos/neg → {pos:50000, neg:50000}
Worker 3: Count pos/neg → {pos:50000, neg:50000}
```

### Phase 3: REDUCE (Master)
```
Worker 1 result: {pos: 50000, neg: 50000}
Worker 2 result: {pos: 50000, neg: 50000}
Worker 3 result: {pos: 50000, neg: 50000}
     ↓
AGGREGATE:
  pos_total = 50000 + 50000 + 50000 = 150000
  neg_total = 50000 + 50000 + 50000 = 150000
```

---

## DOCKER ARCHITECTURE

### Container Network
```
┌─────────────────────────────────────┐
│  sentiment_network (Docker Bridge)   │
│  Internal IP range: 172.18.x.x      │
│                                      │
│  ┌────────────┐  ┌────────────┐     │
│  │ master     │  │ worker1    │     │
│  │ IP:172.... │  │ IP:172.... │     │
│  └────────────┘  │ Port: 5000 │     │
│                  └────────────┘     │
│  ┌────────────┐                     │
│  │ worker2    │                     │
│  │ IP:172.... │                     │
│  │ Port: 5000 │                     │
│  └────────────┘                     │
│  ┌────────────┐                     │
│  │ worker3    │                     │
│  │ IP:172.... │                     │
│  │ Port: 5000 │                     │
│  └────────────┘                     │
└─────────────────────────────────────┘
```

### Port Mapping
```
External Machine (Your PC)    Docker Network    Container
─────────────────────────    ──────────────    ─────────
localhost:5000                               master:5000
localhost:5001          ──→  worker1:5000 ──→ worker:5000
localhost:5002          ──→  worker2:5000 ──→ worker:5000
localhost:5003          ──→  worker3:5000 ──→ worker:5000
```

### DNS Resolution
```
Inside Docker network:
- Master: http://master:5000 (auto-resolved by Docker)
- Worker1: http://worker1:5000
- Worker2: http://worker2:5000
- Worker3: http://worker3:5000

Outside Docker network (your PC):
- Master: http://localhost:5000
- Worker1: http://localhost:5001
- Worker2: http://localhost:5002
- Worker3: http://localhost:5003
```

---

## DATA FLOW DIAGRAM

```
┌─────────────────────────────────┐
│   master/data/mini_data.csv     │
│  (300,000 rows from Sentiment140)│
└──────────────┬──────────────────┘
               ↓
        ┌──────────────┐
        │ Master reads │
        └──────┬───────┘
               ↓
      ┌────────────────┐
      │ Split 300k into │
      │ 3 chunks        │
      └────────┬───────┘
               ↓
      ┌────────┬────────┬────────┐
      ↓        ↓        ↓
   Chunk 1   Chunk 2   Chunk 3
 (100000)  (100000)  (100000)
      ↓        ↓        ↓
  HTTP POST HTTP POST HTTP POST
  5001/process  5002/process  5003/process
      ↓        ↓        ↓
┌────────┐ ┌────────┐ ┌────────┐
│Worker 1│ │Worker 2│ │Worker 3│
│ Pos/Neg│ │ Pos/Neg│ │ Pos/Neg│
└───┬────┘ └───┬────┘ └───┬────┘
    ↓          ↓          ↓
  JSON       JSON       JSON
      └──────────┬──────────┘
                 ↓
        ┌────────────────┐
        │  Master Reduce │
        │  Aggregate sum │
        └────────┬───────┘
                 ↓
        ┌────────────────────────────┐
        │  FINAL RESULTS             │
        │  Positive: 150000 (50.0%) │
        │  Negative: 150000 (50.0%) │
        │  Total: 300,000           │
        └────────┬───────────────────┘
                 ↓
        Save to results/sentiment_results.json
```

---

## KEY CONCEPTS EXPLAINED

### 1. Distributed Computing
- **Single machine simulates multiple machines via Docker**
- Each container has own isolated OS, network interface
- Docker network enables inter-container communication

### 2. MapReduce
- **Map:** Distribute work across workers
- **Reduce:** Collect and combine results
- Enables processing of large datasets in parallel

### 3. Scalability
Current: 3 workers, 300k tweets
Future: 10 workers, 1.6M tweets (same code, just add workers in docker-compose.yml)

### 4. Fault Tolerance
- If worker1 crashes: docker-compose restarts it automatically
- Master can retry failed requests and reassign a chunk to another worker if needed

---

## TECHNOLOGY STACK

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Orchestration | Flask | Lightweight API framework for workers |
| Communication | HTTP/REST | Standard web protocol for data transfer |
| Containerization | Docker | Isolate and run multiple nodes |
| Composition | Docker-Compose | Manage multi-container system |
| Data Processing | Pandas | Load and manipulate CSV data |
| Network | Docker Bridge | Connect containers internally |

---

## PERFORMANCE METRICS

**Current Setup (3 workers, 300k tweets):**
- Total processing time: ~10-20 seconds
- Throughput: ~500-1000 tweets/second

**If scaled to 10 workers, 1.6M tweets:**
- Processing time: ~2-5 minutes (linear with data size)
- Throughput: ~500k tweets/minute

---

## VIVA QUESTIONS & ANSWERS

**Q: Why Docker?**
A: "Simulates distributed system on single machine. Each container is isolated like separate physical machine. Docker network enables IP-based communication between containers."

**Q: Explain the MapReduce flow**
A: "Split phase: Master divides 300k tweets into 3 chunks. Map phase: Each worker processes its chunk independently, counting sentiments. Reduce phase: Master sums results from the workers."

**Q: Why split data?**
A: "Parallel processing. Instead of 1 machine processing 300k rows sequentially, 3 machines process ~100k rows each simultaneously. Faster overall execution."

**Q: How does communication work?**
A: "Workers are Flask servers. Master makes HTTP POST requests to /process endpoint. Workers receive data, process it, return JSON with results."

**Q: What if a worker fails?**
A: "docker-compose has restart policy. If container crashes, it automatically restarts. In production, could queue failed jobs and retry on another worker."

---

**This architecture demonstrates:**
- Distributed systems concepts
- MapReduce paradigm
- Container-based deployment
- IP-based inter-node communication
- Scalable design principles
