import json

# JSONL 파일 경로
jsonl_file_path = 'shuffled_output_responses.jsonl'
output_file_path = 'parsing_output.txt'

# 탐색할 idx의 범위 설정 [start_random_idx, end_random_idx]
start_random_idx = 0
end_random_idx = 999

# 혐오 표현 카테고리 리스트
categories = ['여성/가족', '남성', '성소수자', '인종/국적', '연령', '지역', '종교', '기타 혐오']

# String to store all outputs
output_content = ""

# JSONL 파일 파싱 및 출력
with open(jsonl_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        data = json.loads(line)
        random_idx = data.get('random_idx')
        original_idx = data.get('original_idx')

        # 지정된 idx 범위에 있는 경우만 처리
        if random_idx is not None and start_random_idx <= random_idx <= end_random_idx:
            문장 = data.get('문장', "문장이 없습니다.")
            ans = data.get('ans', "응답이 없습니다.")
            ground_truth = {category: data.get(category, 0) for category in categories}

            # Append the output to the string
            output_content += "\n=========================================\n"
            output_content += f"Processing Entry: random-idx = {random_idx}, original-idx = {original_idx}\n"
            output_content += "=========================================\n\n"

            output_content += "문장 (Sentence):\n"
            output_content += f"  {문장}\n\n"

            output_content += "Ground Truth (혐오 표현 결과):\n"
            for category, value in ground_truth.items():
                output_content += f"  {category}: {value}\n"

            output_content += "\nDetected 혐오 표현 결과 (Detected Hate Speech Results):\n"
            if "혐오표현은 없습니다." in ans:
                output_content += "  혐오표현은 없습니다.\n\n"
            else:
                output_content += "  Detected 표현들:\n"
                lines = ans.split('\n')
                for line in lines:
                    if ':' in line:
                        part, category = line.split(':', 1)
                        output_content += f"    {part.strip()}: {category.strip()}\n"

            output_content += "=========================================\n\n"

# Write the collected output to a file
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(output_content)

print(f"Parsing output has been saved to {output_file_path}")
