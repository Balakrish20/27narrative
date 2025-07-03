import os
import logging
from flask import Flask, request, render_template, jsonify
import pandas as pd
from narrative_utils import build_narrative

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json.get("data", [])
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Define the expected columns
        columns = [
            "regulatory_ID", "case_justification", "case_type", "reporter_type", "publication_title", "country", "IRD",
            "age", "gender", "suspect_drug", "co_suspect_drug", "event", "medical_history", "past_drug_therapy",
            "concurrent_condition", "concomitant_medication", "dose", "frequency", "route", "indication",
            "suspect_drug_start_date"
        ]
        
        # Create DataFrame with proper column handling
        df = pd.DataFrame(data, columns=columns)
        
        # Group by regulatory_ID and generate narratives
        grouped = df.groupby("regulatory_ID")
        results = []
        
        for reg_id, group in grouped:
            try:
                narrative = build_narrative(group)
                results.append({
                    "regulatory_ID": reg_id, 
                    "narrative": narrative
                })
            except Exception as e:
                app.logger.error(f"Error generating narrative for {reg_id}: {str(e)}")
                results.append({
                    "regulatory_ID": reg_id,
                    "narrative": f"Error generating narrative: {str(e)}"
                })
        
        return jsonify({"results": results})
    
    except Exception as e:
        app.logger.error(f"Generation error: {str(e)}")
        return jsonify({"error": f"Generation failed: {str(e)}"}), 400

@app.route('/validate', methods=['POST'])
def validate_data():
    try:
        data = request.json.get("data", [])
        if not data:
            return jsonify({"valid": False, "errors": ["No data provided"]})
        
        errors = []
        required_fields = ["regulatory_ID", "case_justification", "case_type"]
        
        for i, row in enumerate(data):
            for field in required_fields:
                if not row.get(field) or str(row.get(field)).strip() == "":
                    errors.append(f"Row {i+1}: Missing required field '{field}'")
        
        return jsonify({
            "valid": len(errors) == 0,
            "errors": errors
        })
    
    except Exception as e:
        return jsonify({"valid": False, "errors": [str(e)]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
