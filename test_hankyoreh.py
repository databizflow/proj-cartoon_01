import requests
from bs4 import BeautifulSoup

url = 'https://www.hani.co.kr/arti/cartoon/hanicartoon'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f'Status Code: {response.status_code}')
    print(f'Content Length: {len(response.text)}')
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 페이지 제목 확인
    title = soup.find('title')
    if title:
        print(f'Page Title: {title.text.strip()}')
    
    # 만평 관련 요소들 찾기
    selectors = [
        'article',
        '.article-list article',
        '.cartoon-list .item',
        '.list-item',
        'li',
        'div[class*="cartoon"]',
        '.section-list li',
        '.article-list li'
    ]
    
    for selector in selectors:
        items = soup.select(selector)
        if items:
            print(f'{selector}: {len(items)}개 발견')
            if len(items) > 0:
                first_item = items[0]
                print(f'  첫 번째 아이템 텍스트: {first_item.get_text()[:100]}...')
                links = first_item.select('a')
                if links:
                    print(f'  링크 수: {len(links)}')
                    print(f'  첫 번째 링크: {links[0].get("href", "")}')
        else:
            print(f'{selector}: 없음')
    
    # 전체 HTML 구조 확인
    print("\n=== HTML 구조 분석 ===")
    main_content = soup.find('main') or soup.find('div', class_='content') or soup.find('div', id='content')
    if main_content:
        print("메인 콘텐츠 영역 발견")
        articles = main_content.find_all(['article', 'div', 'li'])
        print(f"메인 영역 내 요소 수: {len(articles)}")
        
        for i, article in enumerate(articles[:5]):
            text = article.get_text().strip()[:50]
            if text:
                print(f"  {i+1}: {text}...")
    
except Exception as e:
    print(f'Error: {e}')