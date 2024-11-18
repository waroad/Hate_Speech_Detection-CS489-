import os
import google.generativeai as genai
import pandas as pd

promptTemplate_dir = './prompt_template.txt'
output_answer_dataset = './output_answer_dataset'

model = "gemini-1.5-flash"

genai.configure(api_key="")

def is_right_formatOutput(answer: str):
    categories = [
        "여성/가족",
        "남성",
        "성소수자",
        "인종/국적",
        "연령",
        "지역",
        "종교",
        "기타혐오",
        "악플/욕설",
        "Clean"
    ]
    
    # Check if each category appears with either ':0' or ':1'
    for category in categories:
        if not (f"({category}:0)" in answer or f"({category}:1)" in answer):
            return False
        if f"({category}:0)" in answer and f"({category}:1)" in answer:
            return False
    
    return True

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def query_gemini(prompt):
    """Query the Gemini model with the given prompt."""
    try:
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(prompt)
        return response.text
    except Exception as e:
        #print(f"Error querying Gemini: {e}")
        print("It is a rather sensitive query... please try again.")
        return None
    

if __name__ == "__main__":
    file_path = 'unsmile_valid_v1.0.tsv'
    df = pd.read_csv(file_path, sep='\t')

    response_failed_list = []
    for index, row in df.iterrows():
        prompt = read_file(promptTemplate_dir)
        prompt = prompt.replace('[sentence]', row['문장'])
        
        response = None
        print(f"Querying Gemini for {index}...")
        for i in range(100):
            response = query_gemini(prompt)
            if response and is_right_formatOutput(response):
                output_dir = os.path.join(output_answer_dataset, "right_answer")
                output_file = os.path.join(output_dir, str(index) + ".txt")
                write_file(output_file, response)
                break
            elif response and not is_right_formatOutput(response):
                if i == 99:
                    output_dir = os.path.join(output_answer_dataset, "manualCheck_need_answer")
                    output_file = os.path.join(output_dir, str(index) + ".txt")
                    write_file(output_file, response)
                else:
                    continue
            elif response is None and i == 99:
                output_dir = os.path.join(output_answer_dataset, "failed_answer")
                output_file = os.path.join(output_dir, str(index) + ".txt")
                write_file(output_file, "getting answer was failed because of sensitivity of contents.")
                response_failed_list.append(index)
    
    print("Response failed index list: ")
    print(response_failed_list)
    print("\n\ndone.")
            