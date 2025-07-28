import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hankyoreh_crawl(days=7):
    """한겨레 크롤링 테스트"""
    url = "https://www.hani.co.kr/arti/cartoon/hanicartoon"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        response = session.get(url, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # article 태그로 만평 목록 찾기
        cartoon_items = soup.select('article')
        print(f"한겨레: {len(cartoon_items)}개 article 발견")
        
        if not cartoon_items:
            print("한겨레: 만평 목록을 찾을 수 없습니다")
            return []
        
        results = []
        
        for i, item in enumerate(cartoon_items[:days * 2]):
            try:
                print(f"\n=== 항목 {i+1} 처리 중 ===")
                
                # 제목과 링크
                title_elem = item.select_one('a')
                if not title_elem:
                    print("  링크 없음, 건너뜀")
                    continue
                    
                title = title_elem.get('title') or title_elem.text.strip()
                print(f"  제목: {title}")
                
                if not title or len(title) < 3:
                    print("  제목이 너무 짧음, 건너뜀")
                    continue
                    
                link = title_elem.get('href')
                if not link:
                    print("  href 없음, 건너뜀")
                    continue
                    
                if not link.startswith('http'):
                    link = urljoin(url, link)
                print(f"  링크: {link}")
                
                # 이미지 URL
                img_elem = item.select_one('img')
                img_url = ''
                if img_elem:
                    img_url = img_elem.get('src') or img_elem.get('data-src')
                    if img_url and not img_url.startswith('http'):
                        img_url = urljoin(url, img_url)
                print(f"  이미지: {img_url}")
                
                # 날짜 - 간단하게 추정
                estimated_date = datetime.now() - timedelta(days=i)
                date = estimated_date.strftime('%Y-%m-%d')
                print(f"  날짜: {date}")
                
                # 제목 정리
                clean_title = title.replace('[그림판]', '').replace('[그림마당]', '').strip()
                if not clean_title:
                    clean_title = f"한겨레 그림마당 ({date})"
                print(f"  정리된 제목: {clean_title}")
                
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
                print(f"  ✅ 성공적으로 추가됨")
                
            except Exception as e:
                print(f"  ❌ 항목 {i} 처리 오류: {e}")
                continue
        
        print(f"\n한겨레: {len(results)}개 만평 수집 완료")
        
        # 결과 출력
        print("\n=== 수집된 데이터 ===")
        for i, result in enumerate(results):
            print(f"{i+1}. {result['newspaper']} - {result['date']} - {result['title']}")
        
        return results
        
    except Exception as e:
        print(f"한겨레 크롤링 오류: {e}")
        return []

if __name__ == "__main__":
    results = test_hankyoreh_crawl(5)
    print(f"\n총 {len(results)}개 수집됨")