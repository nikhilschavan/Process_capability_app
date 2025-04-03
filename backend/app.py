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

    # X̄-R Chart
    subgroup_size = 5
    subgroups = [values[i:i + subgroup_size] for i in range(0, len(values), subgroup_size)]
    subgroup_means = [s.mean() for s in subgroups if len(s) == subgroup_size]
    subgroup_ranges = [s.max() - s.min() for s in subgroups if len(s) == subgroup_size]

    plt.figure(figsize=(6, 4))
    plt.plot(subgroup_means, marker='o', linestyle='-')
    plt.title("X̄ Chart")
    xbar_chart_path = os.path.join(UPLOAD_FOLDER, "xbar_chart.png")
    plt.savefig(xbar_chart_path)
    plt.close()

    plt.figure(figsize=(6, 4))
    plt.plot(subgroup_ranges, marker='o', linestyle='-')
    plt.title("R Chart")
    r_chart_path = os.path.join(UPLOAD_FOLDER, "r_chart.png")
    plt.savefig(r_chart_path)
    plt.close()

    #moving range Chart 
    moving_ranges = [abs(values[i] - values[i-1]) for i in range(1, len(values))]

    plt.figure(figsize=(6, 4))
    plt.plot(moving_ranges, marker='o', linestyle='-')
    plt.title("Moving Range Chart")
    moving_range_chart_path = os.path.join(UPLOAD_FOLDER, "moving_range_chart.png")
    plt.savefig(moving_range_chart_path)
    plt.close()

    # I-Chart
    plt.figure(figsize=(6, 4))
    plt.plot(values, marker='o', linestyle='-')
    plt.title("I-Chart")
    ichart_path = os.path.join(UPLOAD_FOLDER, "i_chart.png")
    plt.savefig(ichart_path)
    plt.close()


    return jsonify({
        "Cp": round(Cp, 3),
        "Cpk": round(Cpk, 3),
        "Pp": round(Pp, 3),
        "Ppk": round(Ppk, 3),
        "histogram": "/plot/histogram",
        "xbar_chart": "/plot/xbar_chart",
        "r_chart": "/plot/r_chart",
        "moving_range_chart": "/plot/moving_range_chart",
        "i_chart": "/plot/i_chart"
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
