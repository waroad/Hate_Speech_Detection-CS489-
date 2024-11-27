from flask import Flask, request, jsonify
from flask_cors import CORS  # Add this import

# Flask 애플리케이션 생성
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/process', methods=['POST'])
def process_text():
    # Log the received request data
    data = request.get_json()
    print("Received data:", data)

    input_text = data.get('text', '')
    result = "wowowow2"  # Placeholder response
    print("Returning result:", result)

    return jsonify({"response": result})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
