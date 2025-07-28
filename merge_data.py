import pandas as pd
import json

# 1. 이전 JSON 데이터 로드
with open('1/cartoon_analysis_20250728_143524.json', 'r', encoding='utf-8') as f:
    previous_data = json.load(f)

# JSON을 DataFrame으로 변환
previous_df = pd.DataFrame(previous_data)

print(f"이전 데이터: {len(previous_df)}개")
print("이전 데이터 미리보기:")
print(previous_df[['newspaper', 'date', 'title']].head())

# 2. 현재 CSV 데이터 로드 (있다면)
try:
    current_df = pd.read_csv('data/cartoon_data.csv', encoding='utf-8-sig')
    print(f"\n현재 데이터: {len(current_df)}개")
    print("현재 데이터 미리보기:")
    print(current_df[['newspaper', 'date', 'title']].head())
except FileNotFoundError:
    print("\n현재 데이터 없음")
    current_df = pd.DataFrame()

# 3. 데이터 합치기
if not current_df.empty:
    combined_df = pd.concat([previous_df, current_df], ignore_index=True)
else:
    combined_df = previous_df

print(f"\n합친 데이터: {len(combined_df)}개")

# 4. 중복 제거 (신문사 + 날짜 + 제목 기준)
combined_df = combined_df.drop_duplicates(
    subset=['newspaper', 'date', 'title'], 
    keep='last'
)

print(f"중복 제거 후: {len(combined_df)}개")

# 5. 날짜순 정렬
combined_df['date'] = pd.to_datetime(combined_df['date'])
combined_df = combined_df.sort_values('date', ascending=False)

# 6. 저장
combined_df.to_csv('data/cartoon_data.csv', index=False, encoding='utf-8-sig')

print(f"\n✅ 합쳐진 데이터가 data/cartoon_data.csv에 저장되었습니다!")
print("\n신문사별 분포:")
print(combined_df['newspaper'].value_counts())
print("\n날짜별 분포 (최근 10일):")
print(combined_df['date'].dt.strftime('%Y-%m-%d').value_counts().head(10))