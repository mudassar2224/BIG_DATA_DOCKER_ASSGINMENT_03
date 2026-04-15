# QUICK REFERENCE CHECKLIST

## ALL FILES YOU NEED (8 Total)

```
docker-sentiment-project/
│
├── master/
│   ├── master.py ......................... [Master orchestrator code]
│   ├── requirements.txt .................. [Master dependencies]
│   ├── data/
│   │   └── mini_data.csv ................. [AUTO-CREATED - 300k tweets]
│   └── results/
│       └── sentiment_results.json ........ [AUTO-CREATED - final output]
│
├── worker/
│   ├── worker.py ......................... [Worker processor code]
│   └── requirements.txt .................. [Worker dependencies]
│
├── Dockerfile.master ..................... [Build image for master]
├── Dockerfile.worker ..................... [Build image for worker]
├── docker-compose.yml .................... [Orchestrate containers]
│
└── scripts/
  └── create_mini_dataset.py ............ [Create 300k sample]
```

---

## ASSIGNMENT TASKS COVERAGE

1. System setup
- `docker-compose.yml` creates 1 master container and 3 worker containers (worker1/worker2/worker3)
- All containers are attached to the same Docker bridge network (`sentiment_network`) so each container gets its own IP address

2. Data chunking
- `master.py` splits the dataset into chunks using `split_data(data, num_workers)`
- With 3 workers, the master creates 3 chunks and distributes one chunk per worker (initially)

3. Processing (Map phase)
- Each worker runs `worker.py` (Flask) and processes one chunk at the `/process` endpoint
- Current processing logic: count positive vs negative sentiments in the chunk

4. Aggregation (Reduce phase)
- `master.py` collects each worker's JSON result and aggregates totals
- Final output is written to `master/results/sentiment_results.json`

5. Optional (advanced): node failure + task reassignment
- `master.py` retries and reassigns a chunk to another worker if a worker is unreachable or returns an error
- You can simulate a node failure by stopping one worker container and running again; the master will fall back to the remaining workers

---

## EXECUTION CHECKLIST

### PHASE 1: PREPARATION
- [ ] Install Python 3.9+ (https://python.org)
- [ ] Install Docker Desktop (https://docker.com)
- [ ] Create folder: `docker-sentiment-project`
- [ ] Create subfolders: `master/data`, `worker`, `scripts`, `master/results`

### PHASE 2: CREATE FILES
- [ ] Create `master/master.py` with provided code
- [ ] Create `worker/worker.py` with provided code
- [ ] Create `master/requirements.txt` with pip packages
- [ ] Create `worker/requirements.txt` with flask
- [ ] Create `Dockerfile.master` with Docker config
- [ ] Create `Dockerfile.worker` with Docker config
- [ ] Create `docker-compose.yml` with container config
- [ ] Create `scripts/create_mini_dataset.py` with sampling code

### PHASE 3: DATASET PREPARATION
- [ ] Edit `scripts/create_mini_dataset.py` line 14:
  ```python
  file_path = r"C:\[YOUR_PATH]\training.1600000.processed.noemoticon.csv"
  ```
- [ ] Run: `python scripts/create_mini_dataset.py`
- [ ] Verify: `master/data/mini_data.csv` created (300,000 rows)

### PHASE 4: DOCKER BUILD
- [ ] Start Docker Desktop
- [ ] Run: `docker-compose build`
- [ ] Verify: Both images built successfully

### PHASE 5: EXECUTION
- [ ] Run: `docker-compose up`
- [ ] Wait for master to print final results
- [ ] Verify: `master/results/sentiment_results.json` created

### PHASE 6: VALIDATION
- [ ] Results show positive + negative = 300,000
- [ ] Sentiment percentages calculated correctly
- [ ] No errors in Docker logs

### PHASE 7: DOCUMENTATION (for viva)
- [ ] Create `prompt_log.txt` - Track AI prompts used
- [ ] Create `architecture.md` - System design explanation
- [ ] Create `debugging_report.md` - Issues & fixes
- [ ] Create `viva_notes.md` - Talking points

---

## QUICK COMMANDS

### Directory Setup
```bash
mkdir docker-sentiment-project
cd docker-sentiment-project
mkdir master\data master\results worker scripts
```

### Edit Files
Use Notepad, VS Code, or any text editor to create files

### Prepare Dataset
```bash
python scripts/create_mini_dataset.py
```

### Build Docker
```bash
docker-compose build
```

### Run System
```bash
docker-compose up
```

### View Results
```bash
cat master/results/sentiment_results.json
```

### Stop System
```bash
docker-compose down
```

### Clean Up
```bash
docker-compose down -v
docker system prune
```

---

## EXPECTED OUTPUT

### Step 1: Create Mini Dataset
```
Loaded: 1,600,000 rows
Sampling 300,000 rows...
SUCCESS! Saved to: master/data/mini_data.csv
Dataset Info:
  Total rows: 300000
  Positive: 150000 (50.0%)
  Negative: 150000 (50.0%)
```

### Step 2: Docker Build
```
Building worker
[+] Building 45.2s
Successfully tagged docker-sentiment-project-worker:latest
```

### Step 3: Docker Run
```
sentiment_worker1      | Worker Node starting on 0.0.0.0:5000
sentiment_worker2      | Worker Node starting on 0.0.0.0:5000
sentiment_worker3      | Worker Node starting on 0.0.0.0:5000
sentiment_master       | Loading data...
sentiment_master       | Loaded 300000 rows
...
sentiment_master       | FINAL RESULTS
sentiment_master       | Total tweets processed: 300000
sentiment_master       | Positive sentiment: 150000 (50.0%)
sentiment_master       | Negative sentiment: 150000 (50.0%)
sentiment_master       | Results saved to: results/sentiment_results.json
```

### Step 4: Results File
```json
{
  "positive": 150000,
  "negative": 150000,
  "total": 300000
}
```

---

## COMMON ISSUES & FIXES

| Issue | Solution |
|-------|----------|
| "File not found" | Check file_path in create_mini_dataset.py |
| "Docker not running" | Start Docker Desktop application |
| "Port already in use" | Change ports in docker-compose.yml |
| "Cannot connect to worker" | Wait 5 seconds for containers to start |
| "Request timeout" | Increase timeout in master.py from 30 to 60 seconds |

---

## DOCUMENTATION FILES PROVIDED

1. **SENTIMENT_PROJECT_GUIDE.md** - Project overview
2. **EXECUTION_GUIDE.md** - Step-by-step instructions
3. **ARCHITECTURE_EXPLANATION.md** - System design & viva prep
4. **QUICK_REFERENCE.md** - This file

---

## FILE CONTENTS SUMMARY

### master.py (120 lines)
- Loads CSV data
- Splits data into chunks
- Sends to workers via HTTP
- Aggregates results
- Saves to JSON

### worker.py (40 lines)
- Flask server on port 5000
- Receives data chunks
- Counts positive/negative sentiments
- Returns JSON results

### docker-compose.yml (40 lines)
- Defines 4 services: master, worker1, worker2, worker3
- Sets up Docker network
- Maps ports
- Sets dependencies (master waits for workers)

### Dockerfile.master (12 lines)
- Python 3.9 base image
- Install dependencies
- Copy code and data
- Run master.py

### Dockerfile.worker (12 lines)
- Python 3.9 base image
- Install dependencies
- Copy code
- Run worker.py

### create_mini_dataset.py (60 lines)
- Load full 1.6M dataset
- Extract columns 0 & 5
- Convert labels (4→1)
- Sample 300,000 rows
- Save to CSV

---

## WHAT YOU'RE LEARNING

- **Distributed Systems** - Multiple machines working together
- **MapReduce** - Parallel data processing framework
- **Docker** - Container-based virtualization
- **IP Networking** - Container-to-container communication
- **REST APIs** - HTTP-based data exchange
- **Data Processing** - ETL and aggregation
- **DevOps** - Build, deploy, orchestrate systems

---

## VIVA PREPARATION

**Key Points to Explain:**
1. Why you chose Sentiment140 dataset
2. How MapReduce splits and processes data
3. Why Docker containers simulate distributed system
4. How IP-based communication works
5. What happens if you scale to 10 workers

**Be Ready to Discuss:**
- Errors you faced (and how you fixed them)
- Why you chose Flask for workers
- Performance characteristics (throughput, latency)
- Advantages of distributed processing
- How the system could handle 1.6M tweets

---

## EXPECTED TIME

| Task | Time |
|------|------|
| File creation | 20 min |
| Dataset preparation | 5 min |
| Docker build | 5 min |
| First run | 2 min |
| Documentation | 30 min |
| **TOTAL** | **~60 min** |

---

## SUCCESS CRITERIA

- All 8 files created correctly
- `mini_data.csv` exists with 300,000 rows
- Docker containers build without errors
- System runs and produces sentiment counts
- `sentiment_results.json` matches expected output
- Can explain architecture to instructor

**Once complete:** You have a working distributed sentiment analysis system
ready for presentation!

---

**NEXT STEP:** Start with EXECUTION_GUIDE.md STEP 1!
