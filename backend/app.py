from flask import Flask, request, jsonify, send_file
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return jsonify({"message": "Flask backend is running!"})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Read Excel data
        df = pd.read_excel(filepath)

        # Ensure the required column exists
        column_name = "Measurement"
        if column_name not in df.columns:
            return jsonify({"error": f"Column '{column_name}' not found in file"}), 400

        # Process Capability Calculations
        values = df[column_name].dropna()
        mean_value = values.mean()
        std_dev = values.std()
        Cp = (values.max() - values.min()) / (6 * std_dev)
        Cpk = min((mean_value - values.min()) / (3 * std_dev), (values.max() - mean_value) / (3 * std_dev))
        Pp = (values.max() - values.min()) / (6 * std_dev)
        Ppk = min((mean_value - values.min()) / (3 * std_dev), (values.max() - mean_value) / (3 * std_dev))

        # Generate Histogram
        plt.figure(figsize=(6, 4))
        sns.histplot(values, kde=True, bins=20)
        plt.title("Histogram with KDE")
        histogram_path = os.path.join(UPLOAD_FOLDER, "histogram.png")
        plt.savefig(histogram_path)
        plt.close()

        return jsonify({
            "Cp": round(Cp, 3),
            "Cpk": round(Cpk, 3),
            "Pp": round(Pp, 3),
            "Ppk": round(Ppk, 3),
            "histogram": "/plot/histogram"
        })
    
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

@app.route('/plot/histogram')
def plot_histogram():
    histogram_path = os.path.join(UPLOAD_FOLDER, "histogram.png")
    if os.path.exists(histogram_path):
        return send_file(histogram_path, mimetype='image/png')
    else:
        return jsonify({"error": "Histogram not found"}), 404

if __name__ == '__main__':
    print("🚀 Flask backend is running at http://127.0.0.1:5000/")
    app.run(debug=True)
