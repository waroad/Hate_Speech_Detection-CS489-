import json

# JSONL 파일 경로
jsonl_file_path = 'output_responses.jsonl'

# 탐색할 idx의 범위 설정
start_idx = 2607
end_idx = 2608

# 혐오 표현 카테고리 리스트
categories = ['여성/가족', '남성', '성소수자', '인종/국적', '연령', '지역', '종교', '기타 혐오']

# JSONL 파일 파싱 및 출력
with open(jsonl_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        data = json.loads(line)
        idx = data.get('idx')

        # 지정된 idx 범위에 있는 경우만 처리
        if start_idx <= idx < end_idx:
            문장 = data.get('문장')
            ans = data.get('ans')
            ground_truth = {category: data.get(category) for category in categories}

            print(f"\n--- idx: {idx} ---")
            print(f"문장: {문장}")
            print(f"Ground Truth 혐오 표현 결과: {ground_truth}")

            # 파싱 로직
            if "혐오표현은 없습니다." in ans:
                print("Detected: 혐오표현은 없습니다.")
            else:
                print("Detected 표현들:")
                lines = ans.split('\n')
                for line in lines:
                    if ':' in line:
                        # Split only at the first colon to prevent unpacking issues
                        part, category = line.split(':', 1)
                        print(f"{part.strip()}: {category.strip()}")
