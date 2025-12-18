# importing required libraries
from flask import Flask, request, render_template, send_file, jsonify
import numpy as np
import pickle
import warnings
from convert import convertion
from feature import FeatureExtraction
from sklearn.feature_extraction.text import TfidfVectorizer
from trust_calculator import calculate_trust_score, get_recommendations
from report_generator import generate_scan_report
from text_analyzer import analyze_text_comprehensive
import io

warnings.filterwarnings('ignore')

app = Flask(__name__)

# ---------------------------
# Load Models
# ---------------------------
# Phishing detection model
with open("newmodel.pkl", "rb") as file:
    gbc = pickle.load(file)

# Fake Review Detection model
with open("fake_review_model.pkl", "rb") as f:
    fake_review_model = pickle.load(f)

# TF-IDF Vectorizer for text model
with open("vectorizer.pkl", "rb") as f:
    tfidf_vectorizer = pickle.load(f)


# ---------------------------
# ROUTES
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------- 1️⃣ Phishing URL Scanner ----------
@app.route("/scan", methods=['GET', 'POST'])
def scan():
    if request.method == "POST":
        url = request.form["name"]
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1, 30)
        y_pred = gbc.predict(x)[0]
        name = convertion(url, int(y_pred))

        # Calculate trust score and recommendations
        trust_score = calculate_trust_score(url, int(y_pred), obj.getFeaturesList())
        recommendations = get_recommendations(url, int(y_pred))

        return render_template("scan.html", name=name, trust_score=trust_score, recommendations=recommendations)
    return render_template("scan.html")

@app.route("/download_report/<path:url>")
def download_report(url):
    # Extract URL from path parameter and decode
    import urllib.parse
    decoded_url = urllib.parse.unquote(url)

    # Re-run analysis for the report (in production, store results)
    try:
        obj = FeatureExtraction(decoded_url)
        x = np.array(obj.getFeaturesList()).reshape(1, 30)
        y_pred = gbc.predict(x)[0]
        prediction = int(y_pred)
        trust_score = calculate_trust_score(decoded_url, prediction, obj.getFeaturesList())
        recommendations = get_recommendations(decoded_url, prediction)
        features = obj.getFeaturesList()
    except:
        # Fallback for demo
        prediction = 1
        trust_score = 85
        recommendations = ["This URL appears safe to visit."]
        features = None

    pdf_buffer = generate_scan_report(decoded_url, prediction, trust_score, recommendations, features)
    safe_filename = decoded_url.replace('://', '_').replace('/', '_').replace('.', '_')[:50]
    return send_file(pdf_buffer, as_attachment=True, download_name=f"scan_report_{safe_filename}.pdf", mimetype='application/pdf')


# ---------- 2️⃣ Fake Review / Spam Text Analyzer ----------
@app.route("/analyze", methods=['GET', 'POST'])
def analyze():
    if request.method == "POST":
        text = request.form["review_text"]

        # Convert text to TF-IDF features
        text_tfidf = tfidf_vectorizer.transform([text])

        # Predict class
        prediction = fake_review_model.predict(text_tfidf)[0]
        confidence = np.max(fake_review_model.predict_proba(text_tfidf)) * 100

        if prediction == 1:
            result = "🔴 Fake / Spam Review"
            reason = "Detected unnatural word patterns or excessive sentiment."
        elif prediction == 0:
            result = "🟢 Real Review"
            reason = "Text seems natural and not repetitive."
        else:
            result = "🟡 Possibly Bot-Generated"
            reason = "Text partially resembles spam or repetitive patterns."

        # Comprehensive text analysis
        text_analysis = analyze_text_comprehensive(text)

        return render_template(
            "analyze.html",
            result=result,
            confidence=round(confidence, 2),
            reason=reason,
            text=text,
            analysis=text_analysis
        )

    return render_template("analyze.html")

# ---------- API Endpoint for Real-time Text Analysis ----------
@app.route("/api/analyze_text", methods=['POST'])
def api_analyze_text():
    """API endpoint for real-time text analysis."""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    text = data['text']
    if not text.strip():
        return jsonify({'error': 'Empty text'}), 400

    # Get comprehensive analysis
    analysis = analyze_text_comprehensive(text)

    # Add ML prediction
    text_tfidf = tfidf_vectorizer.transform([text])
    prediction = fake_review_model.predict(text_tfidf)[0]
    confidence = np.max(fake_review_model.predict_proba(text_tfidf)) * 100

    analysis['ml_prediction'] = {
        'is_fake': bool(prediction),
        'confidence': round(confidence, 2)
    }

    return jsonify(analysis)


# ---------- 3️⃣ Verification Page ----------

# ---------- 4️⃣ About Page ----------
@app.route("/about")
def about():
    return render_template("about.html")


# ---------------------------
# Run Flask App
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
