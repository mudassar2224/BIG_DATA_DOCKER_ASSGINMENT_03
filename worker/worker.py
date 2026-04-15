from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    """
    Worker receives data chunk and counts sentiments
    
    Request format:
    {
        "data": [
            [0, "negative tweet"],
            [1, "positive tweet"],
            ...
        ]
    }
    """
    try:
        request_data = request.json
        data = request_data.get('data', [])
        
        positive_count = 0
        negative_count = 0
        
        # Count sentiments
        for row in data:
            sentiment = int(row[0])
            if sentiment == 1:  # Positive (was 4, converted to 1)
                positive_count += 1
            else:  # Negative (0)
                negative_count += 1
        
        result = {
            "positive": positive_count,
            "negative": negative_count,
            "total": len(data)
        }
        
        print(f"Processed {len(data)} rows | Positive: {positive_count} | Negative: {negative_count}")
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    print("Worker Node starting on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
