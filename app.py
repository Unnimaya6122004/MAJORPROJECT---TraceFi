# ===============================
# TraceFi Flask Backend (FINAL)
# Enhanced Report Download
# ===============================

from flask import Flask, jsonify, request, render_template, send_file
import random
import joblib
import pandas as pd
from datetime import datetime
import io
import zipfile
from openpyxl.utils import get_column_letter

# -------------------------------
# Initialize Flask App
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Load Model Artifacts
# -------------------------------
MODEL_PATH = "model/tracefi_rf_model.pkl"
FEATURES_PATH = "model/tracefi_selected_features.pkl"

rf_model = joblib.load(MODEL_PATH)
selected_features = joblib.load(FEATURES_PATH)

print("TraceFi model loaded successfully")

# -------------------------------
# Load Simulation Samples
# -------------------------------
attack_df = pd.read_csv("model/attack_samples_with_type.csv")
benign_df = pd.read_csv("model/benign_samples.csv")

# -------------------------------
# Traffic Counters
# -------------------------------
total_flows = 0
ddos_detected = 0

# -------------------------------
# Attack Logs (for report)
# -------------------------------
attack_logs = []

# ==================================================
# WEBSITE ROUTES
# ==================================================

@app.route("/")
def home_page():
    return render_template("home.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/contact")
def contact_page():
    return render_template("contact.html")

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

# ==================================================
# API ROUTES
# ==================================================

@app.route("/health")
def health():
    return jsonify({
        "status": "TraceFi is running",
        "model_loaded": True,
        "features_used": len(selected_features)
    })

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        input_df = pd.DataFrame([data], columns=selected_features)
        prob = rf_model.predict_proba(input_df)[0][1]
        prediction = "DDoS" if prob >= 0.7 else "Normal"

        return jsonify({
            "prediction": prediction,
            "confidence": round(float(prob), 4)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================================================
# SIMULATED REAL-TIME DETECTION
# ==================================================

@app.route("/simulate", methods=["POST"])
def simulate_detection():
    global total_flows, ddos_detected, attack_logs

    is_attack = random.choice([True, False])

    if is_attack:
        row = attack_df.sample(1).iloc[0]
        attack_type = row["Label"]
        sample = row[selected_features].to_dict()
    else:
        row = benign_df.sample(1).iloc[0]
        attack_type = "Benign"
        sample = row.to_dict()

    prob = rf_model.predict_proba(
        pd.DataFrame([sample])
    )[0][1]

    prediction = "DDoS ATTACK" if prob >= 0.7 else "NORMAL"

    total_flows += 1

    if prediction == "DDoS ATTACK":
        ddos_detected += 1

        # -------------------------------
        # Severity Classification
        # -------------------------------
        if prob >= 0.9:
            severity = "High"
        elif prob >= 0.8:
            severity = "Medium"
        else:
            severity = "Low"

        # Log attack
        attack_logs.append({
            "Flow ID": total_flows,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Prediction": prediction,
            "Attack Type": attack_type,
            "Confidence": round(float(prob), 4),
            "Severity": severity
        })

    detection_rate = round((ddos_detected / total_flows) * 100, 2)

    return jsonify({
        "prediction": prediction,
        "attack_type": attack_type,
        "confidence": round(float(prob), 4),
        "total_flows": total_flows,
        "ddos_detected": ddos_detected,
        "detection_rate": detection_rate
    })

# ==================================================
# DOWNLOAD DETAILED ATTACK REPORT (ZIP)
# ==================================================

@app.route("/download-report")
def download_report():

    if not attack_logs:
        return jsonify({"error": "No attacks detected yet"}), 400

    df = pd.DataFrame(attack_logs).sort_values(
        by=["Confidence", "Timestamp"],
        ascending=[False, True]
    ).reset_index(drop=True)
    df.insert(0, "Incident ID", [f"TRC-{index:04d}" for index in range(1, len(df) + 1)])

    report_generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_attacks = len(df)
    detection_rate = round((total_attacks / total_flows) * 100, 2) if total_flows else 0
    most_common_attack = df["Attack Type"].value_counts().idxmax()
    high_severity_count = len(df[df["Severity"] == "High"])
    avg_confidence = round(float(df["Confidence"].mean()), 4)

    severity_summary = (
        df.groupby("Severity")
        .agg(
            Incident_Count=("Severity", "size"),
            Average_Confidence=("Confidence", "mean"),
            Max_Confidence=("Confidence", "max")
        )
        .reset_index()
        .sort_values(by="Incident_Count", ascending=False)
    )
    severity_summary["Average_Confidence"] = severity_summary["Average_Confidence"].round(4)
    severity_summary["Max_Confidence"] = severity_summary["Max_Confidence"].round(4)

    attack_type_summary = (
        df.groupby("Attack Type")
        .agg(
            Incident_Count=("Attack Type", "size"),
            Average_Confidence=("Confidence", "mean"),
            Highest_Severity=("Severity", lambda values: "High" if "High" in values.values else ("Medium" if "Medium" in values.values else "Low"))
        )
        .reset_index()
        .sort_values(by="Incident_Count", ascending=False)
    )
    attack_type_summary["Average_Confidence"] = attack_type_summary["Average_Confidence"].round(4)

    overview_df = pd.DataFrame([
        {"Metric": "Report Generated On", "Value": report_generated_on},
        {"Metric": "Total Flows Analyzed", "Value": total_flows},
        {"Metric": "Total Attacks Detected", "Value": total_attacks},
        {"Metric": "Detection Rate", "Value": f"{detection_rate}%"},
        {"Metric": "Most Frequent Attack", "Value": most_common_attack},
        {"Metric": "High Severity Attacks", "Value": high_severity_count},
        {"Metric": "Average Confidence", "Value": avg_confidence},
    ])

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    summary_lines = [
        "# TRACEFI DDoS Incident Summary",
        "",
        "## Executive Overview",
        f"- Report generated on: {report_generated_on}",
        f"- Total flows analyzed: {total_flows}",
        f"- Total attacks detected: {total_attacks}",
        f"- Detection rate: {detection_rate}%",
        f"- Most frequent attack type: {most_common_attack}",
        f"- High severity incidents: {high_severity_count}",
        f"- Average confidence score: {avg_confidence}",
        "",
        "## Severity Breakdown",
    ]

    for _, row in severity_summary.iterrows():
        summary_lines.append(
            f"- {row['Severity']}: {int(row['Incident_Count'])} incidents, avg confidence {row['Average_Confidence']}, max confidence {row['Max_Confidence']}"
        )

    summary_lines.extend([
        "",
        "## Attack Type Breakdown",
    ])

    for _, row in attack_type_summary.iterrows():
        summary_lines.append(
            f"- {row['Attack Type']}: {int(row['Incident_Count'])} incidents, avg confidence {row['Average_Confidence']}, highest severity {row['Highest_Severity']}"
        )

    summary_lines.extend([
        "",
        "## Included Files",
        "- tracefi_attack_report.xlsx: multi-sheet workbook with incidents and summaries",
        "- tracefi_attack_report.csv: flat export for quick ingestion",
        "- tracefi_report_summary.md: readable summary for reviews and handoffs",
    ])

    summary_text = "\n".join(summary_lines)

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        overview_df.to_excel(writer, index=False, sheet_name="Overview")
        attack_type_summary.to_excel(writer, index=False, sheet_name="Attack Summary")
        severity_summary.to_excel(writer, index=False, sheet_name="Severity Summary")
        df.to_excel(writer, index=False, sheet_name="Incidents")

        for sheet_name, frame in {
            "Overview": overview_df,
            "Attack Summary": attack_type_summary,
            "Severity Summary": severity_summary,
            "Incidents": df,
        }.items():
            worksheet = writer.sheets[sheet_name]
            for index, column in enumerate(frame.columns, start=1):
                max_len = max(len(str(column)), *(len(str(value)) for value in frame[column].tolist()))
                worksheet.column_dimensions[get_column_letter(index)].width = min(max_len + 3, 28)
            worksheet.freeze_panes = "A2"

    excel_buffer.seek(0)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("tracefi_attack_report.csv", csv_buffer.getvalue())
        zipf.writestr("tracefi_report_summary.md", summary_text)
        zipf.writestr("tracefi_attack_report.xlsx", excel_buffer.getvalue())

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="tracefi_ddos_report.zip"
    )

# -------------------------------
# Run Flask App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
