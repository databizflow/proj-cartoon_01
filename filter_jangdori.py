import pandas as pd

# 현재 데이터 로드
df = pd.read_csv('data/cartoon_data.csv', encoding='utf-8-sig')

print(f"필터링 전 총 데이터: {len(df)}개")
print("\n오마이뉴스 제목들:")
ohmynews_data = df[df['newspaper'] == '오마이뉴스']
for i, title in enumerate(ohmynews_data['title']):
    print(f"{i+1}. {title}")

# 박순찬의 장도리 카툰만 필터링
filtered_df = df.copy()

# 오마이뉴스에서 박순찬 또는 장도리가 포함된 것만 유지
ohmynews_mask = (df['newspaper'] == '오마이뉴스') & (
    df['title'].str.contains('박순찬', na=False) | 
    df['title'].str.contains('장도리', na=False)
)

# 다른 신문사는 그대로 유지
other_newspapers_mask = df['newspaper'] != '오마이뉴스'

# 최종 필터링
filtered_df = df[ohmynews_mask | other_newspapers_mask]

print(f"\n필터링 후 총 데이터: {len(filtered_df)}개")
print(f"제거된 데이터: {len(df) - len(filtered_df)}개")

print("\n필터링 후 신문사별 분포:")
print(filtered_df['newspaper'].value_counts())

print("\n필터링 후 오마이뉴스 제목들:")
filtered_ohmynews = filtered_df[filtered_df['newspaper'] == '오마이뉴스']
for i, title in enumerate(filtered_ohmynews['title']):
    print(f"{i+1}. {title}")

# 저장
filtered_df.to_csv('data/cartoon_data.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ 필터링된 데이터가 저장되었습니다!")