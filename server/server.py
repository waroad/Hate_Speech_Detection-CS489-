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
    device = 0,
    return_all_scores=True,
    function_to_apply='sigmoid'
)

# Load prompt template
PROMPT_TEMPLATE_PATH = './prompt_template.txt'
with open(PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as file:
    prompt_template = file.read()


# Function to query Gemini
def query_gemini(prompt):
    """
    Queries the Gemini model with the given prompt.
    Args:
        prompt (str): The input prompt to send to the model.
    Returns:
        str: The response text from the model.
    """
    try:
        model_instance = genai.GenerativeModel(gemini_model)
        response = model_instance.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error querying Gemini: {e}")
        return None


# Function to parse Gemini's response
def parse_gemini_response(response):
    """
    Parses the Gemini response to extract hate speech localization results.
    Args:
        response (str): The response text from Gemini.
    Returns:
        list: A list of tuples (part, category), where:
              - part (str): The detected text segment.
              - category (str): The associated hate speech category.
    """
    localization_results = []

    if "혐오표현은 없습니다." in response:
        return localization_results  # Return an empty list if no hate speech is detected

    lines = response.split('\n')
    for line in lines:
        if ':' in line:
            part, category = line.split(':', 1)
            localization_results.append((part.strip(), category.strip()))
    return localization_results


# Role 1: Hate expression detection
@app.route('/detect', methods=['POST'])
def detect_hate_expression():
    try:
        data = request.get_json()
        if data['header'] != 'request_detection':
            return jsonify({"error": "Invalid header for detection"}), 400

        sentence = data['sentence']
        detection_results = pipeline(sentence)[0]
        response = {"header": "response_detection", "sentence": sentence}

        for result in detection_results:
            label = result['label']
            score = result['score']
            response[label] = 1 if score >= 0.5 else 0  # Binary classification

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Role 2: Hate expression localization
@app.route('/localize', methods=['POST'])
def localize_hate_expression():
    try:
        data = request.get_json()
        if data['header'] != 'request_localization':
            return jsonify({"error": "Invalid header for localization"}), 400

        sentence = data['sentence']
        detection_results = {label: data[label] for label in data if label not in {'header', 'sentence'}}

        # Create input prompt
        detection_summary = ", ".join([f"{label}: {'있음' if value == 1 else '없음'}" for label, value in detection_results.items()])
        prompt = prompt_template.replace("[sentence]", sentence).replace("[detection]", detection_summary)

        # Query Gemini model
        gemini_response = query_gemini(prompt)
        if not gemini_response:
            return jsonify({"error": "Failed to query Gemini model"}), 500

        # Parse Gemini response to extract localization results
        localization_results = parse_gemini_response(gemini_response)

        # Format localization results with string indices
        result_json = {"header": "respond_localization", 
                       "sentence": sentence, 
                       "num_localization": len(localization_results)}
        for idx, (part, category) in enumerate(localization_results):
            start_idx = sentence.find(part)
            end_idx = start_idx + len(part) if start_idx != -1 else -1
            result_json[idx] = (category, (start_idx, end_idx))

        return jsonify(result_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
