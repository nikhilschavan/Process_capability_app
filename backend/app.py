from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # <-- Import CORS
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)
CORS(app)  # <-- Enable CORS for all routes

@app.route('/')
def home():
    return "Flask backend is running!"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Read Excel data
    df = pd.read_excel(filepath)

    # Ensure the required column exists
    column_name = "Measurement"
    if column_name not in df.columns:
        return jsonify({"error": f"Column '{column_name}' not found in file"}), 400

    # Process Capability Calculations
    values = df[column_name].dropna()
    Cp = (values.mean() - values.min()) / values.std()
    Cpk = min((values.mean() - values.min()) / (3 * values.std()), (values.max() - values.mean()) / (3 * values.std()))
    Pp = (values.max() - values.min()) / (6 * values.std())
    Ppk = min((values.mean() - values.min()) / (3 * values.std()), (values.max() - values.mean()) / (3 * values.std()))

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

@app.route('/plot/histogram')
def plot_histogram():
    histogram_path = os.path.join(UPLOAD_FOLDER, "histogram.png")
    if os.path.exists(histogram_path):
        return send_file(histogram_path, mimetype='image/png')
    else:
        return jsonify({"error": "Histogram not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
