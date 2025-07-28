import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta

def test_fixed_hankyoreh(days=5):
    """수정된 한겨레 크롤링 테스트"""
    url = "https://www.hani.co.kr/arti/cartoon/hanicartoon"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    response = session.get(url, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    cartoon_items = soup.select('article')
    print(f"한겨레: {len(cartoon_items)}개 article 발견")
    
    results = []
    
    for i, item in enumerate(cartoon_items[:days * 2]):
        if len(results) >= days:
            break
            
        try:
            print(f"\n=== 항목 {i+1} 처리 중 ===")
            
            # 모든 링크 찾기
            links = item.find_all('a')
            if not links:
                print("  링크 없음")
                continue
            
            # 텍스트가 있는 링크 찾기
            title_elem = None
            for j, link in enumerate(links):
                text = link.get_text().strip()
                print(f"  링크 {j+1}: '{text}'")
                if text and len(text) > 3:
                    title_elem = link
                    break
            
            if not title_elem:
                print("  유효한 제목 링크 없음")
                continue
                
            title = title_elem.get_text().strip()
            link = title_elem.get('href')
            
            if not link.startswith('http'):
                link = urljoin(url, link)
            
            # 이미지 URL
            img_elem = item.select_one('img')
            img_url = ''
            if img_elem:
                img_url = img_elem.get('src') or img_elem.get('data-src')
                if img_url and not img_url.startswith('http'):
                    img_url = urljoin(url, img_url)
            
            # 날짜
            estimated_date = datetime.now() - timedelta(days=len(results))
            date = estimated_date.strftime('%Y-%m-%d')
            
            # 제목 정리
            clean_title = title.replace('[그림판]', '').replace('[한겨레 그림판]', '').replace('[그림마당]', '').strip()
            if not clean_title:
                clean_title = f"한겨레 그림마당 ({date})"
            
            result = {
                'newspaper': '한겨레',
                'date': date,
                'title': clean_title,
                'image_url': img_url,
                'source_url': link,
                'raw_text': '',
                'summary': clean_title,
                'keywords': ''
            }
            results.append(result)
            
            print(f"  ✅ 성공: {clean_title}")
            
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            continue
    
    print(f"\n한겨레: {len(results)}개 만평 수집 완료")
    
    # 결과 출력
    print("\n=== 수집된 데이터 ===")
    for i, result in enumerate(results):
        print(f"{i+1}. {result['date']} - {result['title']}")
    
    return results

if __name__ == "__main__":
    results = test_fixed_hankyoreh(5)
    print(f"\n총 {len(results)}개 수집됨")