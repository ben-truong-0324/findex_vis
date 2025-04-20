import requests
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    try:
        fastapi_url = "http://mlapi-service/api/ml/data-files"
        print(f"Calling FastAPI at: {fastapi_url}")
        response = requests.get(fastapi_url, timeout=5)
        response.raise_for_status()
        data_files = response.json().get("data_files", [])
        print(f"Fetched data_files: {data_files}")
    except Exception as e:
        print(f"Error fetching data files: {e}")
        data_files = []
    return render_template('index.html', data_files_api=data_files)

@app.route('/data/<path:filename>')
def get_data(filename):
    return send_from_directory('/app/data', filename)


@app.route('/run-prediction', methods=['POST'])
def run_prediction_route():
    print("running pred", flush=True)
    try:
        model_type = request.form.get('model_type', 'Default Decision Tree')
        print(f"🧠 [Flask] Selected model_type: {model_type}", flush=True)

        fastapi_url = "http://mlapi-service/api/ml/run-prediction"
        print(f"📡 [Flask] Sending POST to: {fastapi_url}", flush=True)

        response = requests.post(fastapi_url, json={"model_type": model_type}, timeout=300)
        print(f"✅ [Flask] FastAPI responded with status code: {response.status_code}", flush=True)

        response.raise_for_status()
        data = response.json()
        
        # Write metrics data
        metrics_path = "/app/data/metrics_by_countries.json"
        with open(metrics_path, "w") as f:
            json.dump(data.get("metrics", []), f, indent=2)

        # Write feature importance data
        importance_path = "/app/data/ft_importance.json"
        with open(importance_path, "w") as f:
            json.dump(data.get("feature_importance", []), f, indent=2)

        # Write metrics_list_by_cluster data
        cluster_path = "/app/data/metrics_by_cluster.json"
        with open(cluster_path, "w") as f:
            json.dump(data.get("metrics_list_by_cluster", []), f, indent=2)

        # Redirect to home — D3 will load the new files automatically
        return redirect(url_for("index"))

    except Exception as e:
        return render_template('index.html', prediction_results=[], error=str(e))
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)