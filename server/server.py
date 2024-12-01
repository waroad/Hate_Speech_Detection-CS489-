from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TextClassificationPipeline
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configure Gemini API
genai.configure(api_key="your_api_key")  # Replace with your Gemini API key
gemini_model = "gemini-1.5-flash"  # Specify the Gemini model

# Load pre-trained model and tokenizer for hate speech detection
detection_model = AutoModelForSequenceClassification.from_pretrained("plm")  # Replace "plm" with your model
tokenizer = AutoTokenizer.from_pretrained("beomi/KcELECTRA-base")
pipeline = TextClassificationPipeline(
    model=detection_model,
    tokenizer=tokenizer,
    device=0,  # Use GPU if available
    return_all_scores=True,
    function_to_apply='sigmoid'
)

# Load prompt template
PROMPT_TEMPLATE_PATH = './prompt_template.txt'
with open(PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as file:
    prompt_template = file.read()

# Function to query Gemini
def query_gemini(prompt):
    try:
        model_instance = genai.GenerativeModel(gemini_model)
        response = model_instance.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error querying Gemini: {e}")
        return None

# Function to parse Gemini's response
def parse_gemini_response(response):
    localization_results = []
    if "혐오표현은 없습니다." in response:
        return localization_results  # No hate speech detected
    lines = response.split('\n')
    for line in lines:
        if ':' in line:
            part, category = line.split(':', 1)
            localization_results.append((part.strip(), category.strip()))
    return localization_results

# Unified role: Hate expression detection and localization
@app.route('/inference', methods=['POST'])
def hate_expression_inference():
    try:
        data = request.get_json()
        if data['header'] != 'request_inference':
            return jsonify({"error": "Invalid header for inference"}), 400

        sentence = data['sentence']

        # Step 1: Hate expression detection using PLM
        detection_results = pipeline(sentence)[0]
        detection_summary = {}
        for result in detection_results:
            label = result['label']
            score = result['score']
            detection_summary[label] = 1 if score >= 0.5 else 0  # Binary classification

        # Step 2: Create input prompt for Gemini
        formatted_detection = ", ".join(
            [f"{label}: {'있음' if detection_summary[label] == 1 else '없음'}" for label in detection_summary]
        )
        prompt = prompt_template.replace("[sentence]", sentence).replace("[detection]", formatted_detection)

        # Step 3: Query Gemini model for localization
        gemini_response = query_gemini(prompt)
        if not gemini_response:
            return jsonify({"error": "Failed to query Gemini model"}), 500

        # Step 4: Parse localization results
        localization_results = parse_gemini_response(gemini_response)

        # Step 5: Format localization results with string indices
        result_json = {
            "header": "respond_inference",
            "sentence": sentence,
            "num_localization": len(localization_results),
        }
        for idx, (part, category) in enumerate(localization_results):
            start_idx = sentence.find(part)
            end_idx = start_idx + len(part) if start_idx != -1 else -1
            result_json[idx] = (category, (start_idx, end_idx))

        # Add detection results to response
        result_json.update(detection_summary)

        return jsonify(result_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
