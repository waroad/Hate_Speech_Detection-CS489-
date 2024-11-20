import os
import json
import google.generativeai as genai
import pandas as pd
import tqdm

promptTemplate_dir = './prompt_template.txt'
output_jsonl_file = 'output_responses.jsonl'
inference_results_path = './inference_results.tsv'

model = "gemini-1.5-flash"

genai.configure(api_key="")

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def query_gemini(prompt):
    """Query the Gemini model with the given prompt."""
    try:
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(prompt)
        return response.text
    except Exception as e:
        print("It is a rather sensitive query... please try again.")
        return None

# Load the original dataset and the inference results
file_path = 'unsmile_valid_v1.0.tsv'
df = pd.read_csv(file_path, sep='\t')

inference_df = pd.read_csv(inference_results_path, sep='\t')

response_failed_list = []

with open(output_jsonl_file, 'w', encoding='utf-8') as jsonl_file:
    for index, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        prompt = read_file(promptTemplate_dir)
        prompt = prompt.replace('[sentence]', row['문장'])

        # Get the corresponding inference row
        inference_row = inference_df.loc[index]

        # Format detection output
        detection_labels = ['여성/가족', '남성', '성소수자', '인종/국적', '연령', '지역', '종교', '기타 혐오']
        detection_output = ", ".join([f"{label}: {'있음' if inference_row[label] == 1 else '없음'}"
                                      for label in detection_labels])

        # Replace [detection] in the prompt
        prompt = prompt.replace('[detection]', detection_output)
        
        response = None
        for i in range(100):
            response = query_gemini(prompt)
            if response:
                # Create a dictionary with all relevant information
                output_data = row.to_dict()
                output_data['idx'] = index
                output_data['ans'] = response

                # Write to JSONL file
                jsonl_file.write(json.dumps(output_data, ensure_ascii=False) + '\n')
                break
            elif response is None and i == 99:
                response_failed_list.append(index)
                # Create a failed response entry
                output_data = row.to_dict()
                output_data['idx'] = index
                output_data['ans'] = "getting answer was failed because of sensitivity of contents."
                jsonl_file.write(json.dumps(output_data, ensure_ascii=False) + '\n')

print("Response failed index list: ")
print(response_failed_list)
print("\n\ndone.")
