# Hate Speech Detection and Localization System (CS489)

## Introduction
This project is designed to detect and localize hate speech using advanced machine learning models and natural language processing. The system integrates a Chrome extension, server-side inference, and a robust evaluation pipeline to highlight and categorize hate expressions in text.

Key features include a user-friendly interface, machine learning-powered detection, and support for advanced generative AI models (e.g., Gemini).

---

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Configuration](#configuration)
---

## Features
- **Chrome Extension**: Allows users to select and analyze text directly on web pages.
- **Server-Side ML Inference**: Employs transformers and pre-trained language models (e.g., KcELECTRA) for hate speech classification.
- **Hate Speech Localization**: Identifies specific parts of the text associated with hate speech categories.
- **API Integration**: Incorporates generative AI (e.g., Gemini) for advanced localization tasks.
- **Performance Metrics**: Evaluates precision, recall, and F1-scores for model accuracy.
- **Dataset Preprocessing**: Includes tools for shuffling, parsing, and cleaning data for experiments.

---

## Installation

### Chrome Extension
1. Navigate to the `chrome extension` directory.
2. Load the extension into Chrome:
   - Go to `chrome://extensions`.
   - Enable Developer mode.
   - Click **Load unpacked** and select the `chrome extension` folder.

### Server Setup
1. Install Python 3.7+ and virtual environment tools:
   ```bash
   pip install -r requirements.txt

2. Run the server:
    ```bash
   python server.py

## Usage
Chrome Extension
1. Select text on a web page.
2. Right-click and choose Analyze this text.
3. The extension will highlight hate speech in the selected text.

## Command-Line Evaluation
To compute evaluation metrics:
    ```bash
   python calculate_metric.py

## Advanced Features
- **Shuffling Dataset**:
    ```bash
    python shuffle_jsonl.py
- **Gemini-based Localization**: 
    ```bash
    python generate_answer.py

## Configuration
- **API Key**
    Set up your Gemini API key in the `options.html` interface. Alternatively, configure it directly in `gemini_answer_generation.py` and `server.py`.
- **Customization**: 
    ```bash
    Edit the `prompt_template.txt` to modify hate speech definitions or categories.
