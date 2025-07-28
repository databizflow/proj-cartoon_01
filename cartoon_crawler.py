import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
from datetime import datetime, timedelta
import json
from urllib.parse import urljoin, urlparse
import logging
import os
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CartoonCrawler:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 데이터 디렉토리 생성
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
    def setup_selenium(self):
        """Selenium 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            return webdriver.Chrome(options=chrome_options)
        except Exception as e:
            logger.error(f"Selenium 설정 실패: {e}")
            logger.info("ChromeDriver가 설치되어 있는지 확인해주세요.")
            return None
    
    def analyze_site_feasibility(self, url):
        """사이트 크롤링 가능성 분석"""
        try:
            response = self.session.head(url, timeout=10)
            
            if response.status_code != 200:
                return False, f"HTTP {response.status_code} 오류"
                
            return True, "크롤링 가능"
            
        except Exception as e:
            return False, f"접근 불가: {str(e)}"
    
    def crawl_ohmynews(self, days=7):
        """오마이뉴스 크롤링"""
        url = "https://www.ohmynews.com/NWS_Web/ArticlePage/Cartoon/Cartoon_List.aspx"
        
        feasible, reason = self.analyze_site_feasibility(url)
        if not feasible:
            logger.error(f"오마이뉴스: {reason}")
            return []
        
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            
            # 다양한 셀렉터로 만평 링크 찾기
            selectors = [
                'a[href*="View"]',
                '.cartoon_list a',
                '.list_item a',
                'td a[href*="ArticleView"]'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    logger.info(f"오마이뉴스: {selector}로 {len(links)}개 링크 발견")
                    break
            
            if not links:
                # 텍스트 기반 검색
                links = soup.find_all('a', href=True)
                links = [link for link in links if any(keyword in link.get_text() for keyword in ['장도리', '만평', '카툰'])]
            
            count = 0
            for link in links[:days * 2]:  # 여유있게 수집
                if count >= days:
                    break
                    
                try:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if not text or len(text) < 3:
                        continue
                    
                    # 박순찬의 장도리 카툰만 필터링
                    if not any(keyword in text for keyword in ['박순찬', '장도리']):
                        continue
                    
                    # 상세 페이지 링크 구성
                    if not href.startswith('http'):
                        detail_url = urljoin(url, href)
                    else:
                        detail_url = href
                    
                    # 날짜 추출
                    date_match = re.search(r'(\d{2}[./]\d{2}[./]\d{2})', text)
                    if date_match:
                        date_str = date_match.group(1).replace('.', '-').replace('/', '-')
                        parts = date_str.split('-')
                        if len(parts) == 3 and len(parts[0]) == 2:
                            date = f"20{parts[0]}-{parts[1]}-{parts[2]}"
                        else:
                            date = datetime.now().strftime('%Y-%m-%d')
                    else:
                        # 순차적으로 날짜 할당
                        estimated_date = datetime.now() - timedelta(days=count)
                        date = estimated_date.strftime('%Y-%m-%d')
                    
                    # 제목 정리
                    title = re.sub(r'\d{2}[./]\d{2}[./]\d{2}\s*\d{2}:\d{2}', '', text).strip()
                    if not title:
                        title = f"장도리 ({date})"
                    
                    result = {
                        'newspaper': '오마이뉴스',
                        'date': date,
                        'title': title,
                        'image_url': '',
                        'source_url': detail_url,
                        'raw_text': '',
                        'summary': '',
                        'keywords': ''
                    }
                    
                    # 이미지 URL 추출
                    try:
                        detail_response = self.session.get(detail_url, timeout=10)
                        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                        
                        # 이미지 찾기
                        img_selectors = ['img[src*="cartoon"]', 'img[src*="image"]', '.article_content img', 'img']
                        for img_selector in img_selectors:
                            img_tag = detail_soup.select_one(img_selector)
                            if img_tag and img_tag.get('src'):
                                img_src = img_tag.get('src')
                                if img_src and not img_src.startswith('http'):
                                    result['image_url'] = urljoin(detail_url, img_src)
                                else:
                                    result['image_url'] = img_src
                                break
                        
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.warning(f"오마이뉴스 이미지 추출 실패: {e}")
                    
                    results.append(result)
                    count += 1
                    
                except Exception as e:
                    logger.error(f"오마이뉴스 항목 처리 오류: {e}")
                    continue
            
            logger.info(f"오마이뉴스: {len(results)}개 만평 수집 완료")
            return results
            
        except Exception as e:
            logger.error(f"오마이뉴스 크롤링 오류: {e}")
            return []
    
    def crawl_hankyoreh(self, days=7):
        """한겨레 크롤링 - 수정된 버전"""
        url = "https://www.hani.co.kr/arti/cartoon/hanicartoon"
        
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # article 태그로 만평 목록 찾기
            cartoon_items = soup.select('article')
            logger.info(f"한겨레: {len(cartoon_items)}개 article 발견")
            
            if not cartoon_items:
                logger.warning("한겨레: 만평 목록을 찾을 수 없습니다")
                return []
            
            results = []
            
            for i, item in enumerate(cartoon_items[:days * 2]):
                if len(results) >= days:
                    break
                    
                try:
                    # 모든 링크 찾기 (한겨레는 article당 2개 링크가 있음)
                    links = item.find_all('a')
                    if not links:
                        continue
                    
                    # 텍스트가 있는 링크 찾기 (보통 두 번째 링크)
                    title_elem = None
                    for link in links:
                        text = link.get_text().strip()
                        if text and len(text) > 3:
                            title_elem = link
                            break
                    
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text().strip()
                    link = title_elem.get('href')
                    
                    if not link:
                        continue
                    if not link.startswith('http'):
                        link = urljoin(url, link)
                    
                    # 이미지 URL (img 태그의 alt 속성도 확인)
                    img_elem = item.select_one('img')
                    img_url = ''
                    if img_elem:
                        img_url = img_elem.get('src') or img_elem.get('data-src')
                        if img_url and not img_url.startswith('http'):
                            img_url = urljoin(url, img_url)
                        
                        # alt 속성에서 제목 보완
                        if not title and img_elem.get('alt'):
                            title = img_elem.get('alt').strip()
                    
                    if not title or len(title) < 3:
                        continue
                    
                    # 날짜 - 순차적으로 추정
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
                    
                except Exception as e:
                    logger.error(f"한겨레 항목 {i} 처리 오류: {e}")
                    continue
            
            logger.info(f"한겨레: {len(results)}개 만평 수집 완료")
            return results
            
        except Exception as e:
            logger.error(f"한겨레 크롤링 오류: {e}")
            return []
    
    def crawl_kyunghyang(self, days=7):
        """경향신문 크롤링"""
        url = "https://www.khan.co.kr/cartoon"
        
        feasible, reason = self.analyze_site_feasibility(url)
        if not feasible:
            logger.error(f"경향신문: {reason}")
            return []
        
        try:
            # requests로 먼저 시도
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 만평 목록 찾기
            selectors = [
                '.cartoon-item',
                '.list-item',
                'article',
                '.cartoon_list li',
                'li'
            ]
            
            cartoons = []
            for selector in selectors:
                items = soup.select(selector)
                if items and len(items) > 3:
                    cartoons = items
                    logger.info(f"경향신문: {selector}로 {len(items)}개 아이템 발견")
                    break
            
            if not cartoons:
                # Selenium으로 시도
                driver = self.setup_selenium()
                if driver:
                    try:
                        driver.get(url)
                        time.sleep(3)
                        cartoons = driver.find_elements(By.CSS_SELECTOR, ".cartoon-item, .list-item, article, li")
                    except Exception as e:
                        logger.error(f"Selenium 크롤링 실패: {e}")
                    finally:
                        driver.quit()
            
            results = []
            for i, cartoon in enumerate(cartoons[:days * 2]):
                if len(results) >= days:
                    break
                    
                try:
                    if hasattr(cartoon, 'select_one'):  # BeautifulSoup 객체
                        title_elem = cartoon.select_one('a')
                        if title_elem:
                            title = title_elem.get('title') or title_elem.text.strip()
                            link = title_elem.get('href')
                        else:
                            continue
                            
                        img_elem = cartoon.select_one('img')
                        if img_elem:
                            img_url = img_elem.get('src')
                        else:
                            img_url = ''
                    else:  # Selenium 객체
                        try:
                            title_elem = cartoon.find_element(By.CSS_SELECTOR, "a")
                            title = title_elem.get_attribute("title") or title_elem.text.strip()
                            link = title_elem.get_attribute("href")
                            
                            img_elem = cartoon.find_element(By.CSS_SELECTOR, "img")
                            img_url = img_elem.get_attribute("src")
                        except:
                            continue
                    
                    if not title or len(title) < 3:
                        continue
                    
                    # 만평 관련 필터링
                    if not any(keyword in title for keyword in ['김용민', '그림마당', '만평']):
                        continue
                    
                    if img_url and not img_url.startswith('http'):
                        img_url = urljoin(url, img_url)
                    
                    # 날짜 설정
                    estimated_date = datetime.now() - timedelta(days=len(results))
                    date = estimated_date.strftime('%Y-%m-%d')
                    
                    result = {
                        'newspaper': '경향신문',
                        'date': date,
                        'title': title,
                        'image_url': img_url,
                        'source_url': link if link and link.startswith('http') else urljoin(url, link or ''),
                        'raw_text': '',
                        'summary': '',
                        'keywords': ''
                    }
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"경향신문 항목 처리 오류: {e}")
                    continue
            
            logger.info(f"경향신문: {len(results)}개 만평 수집 완료")
            return results
            
        except Exception as e:
            logger.error(f"경향신문 크롤링 오류: {e}")
            return []
    
    def analyze_content_and_keywords(self, title, newspaper, date):
        """제목과 메타데이터를 바탕으로 키워드 분석"""
        keywords = []
        
        # 제목 기반 키워드 추출
        if title:
            keyword_mapping = {
                '내란': ['내란', '정치', '대통령', '헌법'],
                '탄핵': ['탄핵', '정치', '대통령', '국회'],
                '대통령': ['대통령', '정치', '청와대'],
                '경호': ['경호', '보안', '정치'],
                '구속': ['구속', '법무', '정치', '검찰'],
                '옥중': ['구속', '법무', '감옥'],
                '기각': ['법원', '재판', '법무'],
                '견마지로': ['정치', '사회'],
                '여론': ['여론', '정치', '사회'],
                '정부': ['정부', '정치', '행정'],
                '국회': ['국회', '정치', '의회'],
                '경제': ['경제', '금융', '시장'],
                '부동산': ['부동산', '경제', '주택'],
                '물가': ['물가', '경제', '인플레이션'],
                '환율': ['환율', '경제', '달러'],
                '북한': ['북한', '외교', '안보'],
                '중국': ['중국', '외교', '국제'],
                '일본': ['일본', '외교', '국제'],
                '미국': ['미국', '외교', '국제'],
                '교육': ['교육', '사회', '학교'],
                '의료': ['의료', '보건', '사회'],
                '환경': ['환경', '기후', '사회'],
                '코로나': ['코로나', '방역', '보건']
            }
            
            title_lower = title.lower()
            for keyword, related_terms in keyword_mapping.items():
                if keyword in title_lower:
                    keywords.extend(related_terms)
        
        # 신문사별 특성 키워드
        newspaper_keywords = {
            '오마이뉴스': ['정치', '사회', '시민'],
            '한겨레': ['정치', '경제', '진보'],
            '경향신문': ['정치', '사회', '언론']
        }
        
        if newspaper in newspaper_keywords:
            keywords.extend(newspaper_keywords[newspaper])
        
        # 시기별 키워드 (2025년 7월 기준)
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            if date_obj.month == 7 and date_obj.year == 2025:
                if date_obj.day >= 20:
                    keywords.extend(['여름', '정치', '국정'])
                elif date_obj.day >= 10:
                    keywords.extend(['중순', '사회', '경제'])
        except:
            pass
        
        # 중복 제거 및 최대 5개 선택
        unique_keywords = []
        for k in keywords:
            if k not in unique_keywords:
                unique_keywords.append(k)
        
        return unique_keywords[:5]
    
    def generate_summary_and_keywords(self, title, newspaper, date):
        """제목을 바탕으로 요약과 키워드 생성"""
        # 키워드 분석
        keywords = self.analyze_content_and_keywords(title, newspaper, date)
        
        # 요약 생성
        if title and len(title) > 5:
            if len(title) > 50:
                summary = title[:47] + "..."
            else:
                summary = title
        else:
            summary = f"{newspaper} 만평 ({date})"
        
        return summary, ", ".join(keywords)
    
    def crawl_all_sites(self, days=7):
        """모든 사이트 크롤링"""
        logger.info(f"크롤링 시작... (최근 {days}일)")
        
        all_results = []
        
        # 각 사이트별 크롤링
        crawlers = [
            ('오마이뉴스', self.crawl_ohmynews),
            ('한겨레', self.crawl_hankyoreh),
            ('경향신문', self.crawl_kyunghyang)
        ]
        
        for name, crawler_func in crawlers:
            logger.info(f"{name} 크롤링 중...")
            try:
                results = crawler_func(days)
                all_results.extend(results)
                logger.info(f"{name}: {len(results)}개 항목 수집")
                time.sleep(2)  # 서버 부하 방지
            except Exception as e:
                logger.error(f"{name} 크롤링 실패: {e}")
        
        # 분석 수행
        logger.info("콘텐츠 분석 중...")
        for result in all_results:
            summary, keywords = self.generate_summary_and_keywords(
                result['title'], 
                result['newspaper'], 
                result['date']
            )
            result['summary'] = summary
            result['keywords'] = keywords
        
        # 날짜순 정렬
        all_results.sort(key=lambda x: x['date'], reverse=True)
        
        self.results = all_results
        logger.info(f"크롤링 완료: 총 {len(all_results)}개 항목")
        return all_results
    
    def save_results(self, filename='cartoon_data'):
        """결과를 CSV로 저장 (기존 데이터와 합치기)"""
        if not self.results:
            logger.warning("저장할 데이터가 없습니다.")
            return None
        
        # 새 데이터 DataFrame
        new_df = pd.DataFrame(self.results)
        
        # 고정 파일명
        csv_filename = self.data_dir / f"{filename}.csv"
        
        # 기존 데이터가 있으면 로드
        if csv_filename.exists():
            try:
                existing_df = pd.read_csv(csv_filename, encoding='utf-8-sig')
                logger.info(f"기존 데이터 {len(existing_df)}개 로드")
                
                # 기존 데이터와 새 데이터 합치기
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                
                # 중복 제거 (신문사 + 날짜 + 제목 기준)
                combined_df = combined_df.drop_duplicates(
                    subset=['newspaper', 'date', 'title'], 
                    keep='last'  # 최신 데이터 유지
                )
                
                logger.info(f"중복 제거 후 총 {len(combined_df)}개")
                
            except Exception as e:
                logger.warning(f"기존 데이터 로드 실패: {e}, 새 데이터만 저장")
                combined_df = new_df
        else:
            logger.info("새 파일 생성")
            combined_df = new_df
        
        # 날짜순 정렬
        combined_df = combined_df.sort_values('date', ascending=False)
        
        # CSV 저장
        combined_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        logger.info(f"데이터 저장 완료: {csv_filename}")
        
        # 통계 출력
        print(f"\n=== 수집 결과 통계 ===")
        print(f"총 저장 항목: {len(combined_df)}개")
        print(f"새로 추가: {len(new_df)}개")
        print(f"\n신문사별 분포:")
        print(combined_df['newspaper'].value_counts())
        print(f"\n날짜별 분포 (최근 10일):")
        print(combined_df['date'].value_counts().head(10))
        
        return combined_df
    
    def get_latest_data(self):
        """가장 최근 저장된 데이터 불러오기"""
        csv_files = list(self.data_dir.glob("cartoon_analysis_*.csv"))
        if not csv_files:
            return None
        
        # 가장 최근 파일 선택
        latest_file = max(csv_files, key=os.path.getctime)
        df = pd.read_csv(latest_file, encoding='utf-8-sig')
        logger.info(f"최근 데이터 로드: {latest_file}")
        return df

# 사용 예시 및 메인 함수
def main():
    """메인 실행 함수"""
    print("=== 시사만평 크롤러 ===")
    print("국내 주요 신문사 만평을 수집합니다.")
    
    crawler = CartoonCrawler()
    
    # 사용자 입력
    try:
        days = int(input("수집할 날짜 수를 입력하세요 (기본값: 7): ") or "7")
    except:
        days = 7
    
    print(f"\n최근 {days}일간의 만평을 수집합니다...")
    
    # 크롤링 실행
    results = crawler.crawl_all_sites(days=days)
    
    if results:
        # 결과 저장
        df = crawler.save_results('cartoon_data')
        
        # 결과 미리보기
        if df is not None and not df.empty:
            print("\n=== 수집 결과 미리보기 ===")
            preview_df = df[['newspaper', 'date', 'title', 'keywords']].head(10)
            print(preview_df.to_string(index=False))
            
            print(f"\n데이터가 'data' 폴더에 저장되었습니다.")
            print("Streamlit 대시보드를 실행하려면 다음 명령어를 사용하세요:")
            print("streamlit run dashboard.py")
    else:
        print("수집된 데이터가 없습니다. 네트워크 연결이나 사이트 접근을 확인해주세요.")

if __name__ == "__main__":
    main()