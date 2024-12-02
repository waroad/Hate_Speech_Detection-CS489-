from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TextClassificationPipeline
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configure Gemini API
genai.configure(api_key="AIzaSyAK30nCONzlj-ozSB19Y2BcZBBFtDJikDQ")  # Replace with your Gemini API key
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
            localization_results.append((part.strip('[]').strip(), category.strip('[]').strip()))
    return localization_results

# Unified role: Hate expression detection and localization
@app.route('/inference', methods=['POST'])
def hate_expression_inference():
    data = request.get_json(force=True)
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
        "sentence": sentence
    }
    localization_list = []
    for part, category in localization_results:
        localization_point = []
        start_idx = sentence.find(part)
        end_idx = start_idx + len(part) if start_idx != -1 else -1
        localization_point.append(category)
        localization_point.append(start_idx)
        localization_point.append(end_idx)
        localization_list.append(localization_point)
        print(sentence[start_idx:end_idx])
    result_json['localization_list'] = localization_list

    # Add detection results to response
    #result_json.update(detection_summary)

    #print(jsonify(result_json))
    print(result_json)
    return jsonify(result_json)


# Run the server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
