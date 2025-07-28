import requests
from bs4 import BeautifulSoup

url = 'https://www.hani.co.kr/arti/cartoon/hanicartoon'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

articles = soup.select('article')
print(f"총 {len(articles)}개 article 발견")

for i, article in enumerate(articles[:3]):
    print(f"\n=== Article {i+1} ===")
    print("HTML 구조:")
    print(article.prettify()[:500])
    print("...")
    
    # 모든 링크 찾기
    links = article.find_all('a')
    print(f"\n링크 수: {len(links)}")
    for j, link in enumerate(links):
        print(f"  링크 {j+1}:")
        print(f"    href: {link.get('href', 'None')}")
        print(f"    title: {link.get('title', 'None')}")
        print(f"    text: '{link.get_text().strip()}'")
    
    # 모든 텍스트 추출
    all_text = article.get_text().strip()
    print(f"\n전체 텍스트: '{all_text[:100]}...'")
    
    # h 태그들 찾기
    headers = article.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if headers:
        print(f"\n헤더 태그들:")
        for h in headers:
            print(f"  {h.name}: '{h.get_text().strip()}'")
    
    print("-" * 50)