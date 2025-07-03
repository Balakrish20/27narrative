import os
import logging
from flask import Flask, request, render_template, jsonify
from datetime import datetime
from dateutil import parser

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

def get_value_or_default(val, default="unknown"):
    """Get value or return default if value is None, empty, or whitespace-only"""
    if val is None or str(val).strip() == "" or str(val).lower() == "nan":
        return default
    return str(val).strip()

def join_items(lst):
    """Join list items with proper grammar (commas and 'and')"""
    lst = [i for i in lst if i]
    if len(lst) == 1: 
        return lst[0]
    elif len(lst) == 2: 
        return f"{lst[0]} and {lst[1]}"
    elif len(lst) > 2: 
        return ", ".join(lst[:-1]) + f", and {lst[-1]}"
    return ""

def build_narrative_simple(data_rows):
    """Build narrative from regulatory data rows"""
    if not data_rows:
        return "No data provided for narrative generation."
    
    # Use first row for basic information
    row = data_rows[0]
    
    # Extract basic case information
    regulatory_ID = get_value_or_default(row.get("regulatory_ID"))
    case_justification = get_value_or_default(row.get("case_justification"))
    case_type = get_value_or_default(row.get("case_type"))
    reporter = get_value_or_default(row.get("reporter_type")).lower()
    title = get_value_or_default(row.get("publication_title"))
    country = get_value_or_default(row.get("country"))
    ird = get_value_or_default(row.get("IRD"))

    # Format IRD date
    try:
        ird_fmt = parser.parse(ird).strftime("%d-%b-%Y").upper()
    except:
        ird_fmt = "unknown"

    # Process suspect drugs
    suspect_list = []
    for data_row in data_rows:
        suspect = get_value_or_default(data_row.get("suspect_drug"))
        if suspect != "unknown" and suspect not in suspect_list:
            suspect_list.append(suspect)
    
    suspect_text = join_items(suspect_list) if suspect_list else "(no suspect drugs listed)"
    manufacturer_text = "(unknown manufacturer)" if len(suspect_list) <= 1 else "(unknown manufacturers)"
    cosuspect = get_value_or_default(row.get("co_suspect_drug"))
    event = get_value_or_default(row.get("event"))

    # Format age and gender
    age_raw = get_value_or_default(row.get("age"), "")
    gender_raw = get_value_or_default(row.get("gender"), "")
    age_known = age_raw.lower() not in ["", "unknown", "nan"]
    gender_known = gender_raw.lower() not in ["", "unknown", "nan"]

    if age_known:
        try:
            age_int = int(float(age_raw))
            age_article = "an" if str(age_int)[0] in "8" else "a"
            age_phrase = f"{age_article} {age_int}-year-old"
        except:
            age_phrase = ""
    else:
        age_phrase = ""

    if age_known and gender_known:
        patient_description = f"{age_phrase} {gender_raw.lower()} patient"
    elif age_known and not gender_known:
        patient_description = f"{age_phrase} patient (unknown gender)"
    elif not age_known and gender_known:
        gender_article = "an" if gender_raw.lower().startswith(('a', 'e', 'i', 'o', 'u')) else "a"
        patient_description = f"{gender_article} {gender_raw.lower()} patient (unknown age)"
    else:
        patient_description = "patient (unknown demographics)"

    # Paragraph 1 - Case Overview
    p1 = f"This {case_justification} case was reported by a {reporter} with medical literature \"{title}\", from {country}. "
    p1 += f"This case was received by Alkem on {ird_fmt} from {case_type} with {regulatory_ID}. "
    p1 += f"It concerns {patient_description}, who was administered {suspect_text} {manufacturer_text}. "
    p1 += f"The co-suspect drug was {cosuspect}. The patient experienced {event}."

    # Paragraph 2 - Patient History
    fields = {
        "medical history": [get_value_or_default(r.get("medical_history")) for r in data_rows],
        "past drug therapy": [get_value_or_default(r.get("past_drug_therapy")) for r in data_rows],
        "concurrent conditions": [get_value_or_default(r.get("concurrent_condition")) for r in data_rows],
        "concomitant medications": [get_value_or_default(r.get("concomitant_medication")) for r in data_rows]
    }

    para2_parts = []
    not_reported = []

    for label, values in fields.items():
        values = [v for v in values if v != "unknown"]
        if values:
            phrase_label = label if len(values) > 1 else label.rstrip("s")
            para2_parts.append(f"{phrase_label} included {join_items(values)}")
        else:
            not_reported.append(label)

    if para2_parts:
        p2 = f"The patient's {'. '.join(para2_parts)}."
    else:
        p2 = ""

    if not_reported:
        missing_info = f"The {join_items(not_reported)} were not reported."
        p2 = f"{p2} {missing_info}".strip()

    # Paragraph 3 - Drug Administration Details
    drug_lines = []
    for r in data_rows:
        date = get_value_or_default(r.get("suspect_drug_start_date"))
        try:
            date_fmt = parser.parse(date).strftime("%d-%b-%Y").upper()
        except:
            date_fmt = "unknown date"
        drug = get_value_or_default(r.get("suspect_drug"))
        dose = get_value_or_default(r.get("dose"))
        freq = get_value_or_default(r.get("frequency"))
        route = get_value_or_default(r.get("route"))
        indication = get_value_or_default(r.get("indication"), "an unknown indication")
        line = f"On {date_fmt}, the patient was administered {drug} at the dose of {dose}, frequency {freq}, via {route} for {indication}."
        drug_lines.append(line)

    if len(drug_lines) == 1:
        drug_lines.append("The batch number and expiration date were not reported.")
    elif len(drug_lines) > 1:
        drug_lines.append("The batch numbers and expiration dates were not reported.")

    p3 = " ".join(drug_lines)
    return f"{p1}\n\n{p2}\n\n{p3}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        if not data or not data.get("data"):
            return jsonify({"error": "No data provided"}), 400
        
        input_data = data.get("data", [])
        
        # Group by regulatory_ID manually
        grouped_data = {}
        for row in input_data:
            reg_id = row.get("regulatory_ID", "unknown")
            if reg_id not in grouped_data:
                grouped_data[reg_id] = []
            grouped_data[reg_id].append(row)
        
        results = []
        for reg_id, group_rows in grouped_data.items():
            try:
                narrative = build_narrative_simple(group_rows)
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
        data = request.json
        if not data or not data.get("data"):
            return jsonify({"valid": False, "errors": ["No data provided"]})
        
        input_data = data.get("data", [])
        errors = []
        required_fields = ["regulatory_ID", "case_justification", "case_type"]
        
        for i, row in enumerate(input_data):
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