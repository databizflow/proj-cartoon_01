"""
시사만평 크롤러 설정 파일

사용자가 쉽게 설정을 변경할 수 있도록 만든 설정 파일입니다.
"""

# 크롤링 대상 사이트 설정
NEWSPAPER_SITES = {
    '오마이뉴스': {
        'name': '오마이뉴스',
        'cartoon_name': '박순찬의 장도리',
        'url': 'https://www.ohmynews.com/NWS_Web/ArticlePage/Cartoon/Cartoon_List.aspx',
        'mobile_url': 'https://m.ohmynews.com/NWS_Web/Mobile/comics.aspx',
        'enabled': True
    },
    '한겨레': {
        'name': '한겨레',
        'cartoon_name': '김성곤의 그림마당',
        'url': 'https://www.hani.co.kr/arti/cartoon/hanicartoon',
        'enabled': True
    },
    '경향신문': {
        'name': '경향신문',
        'cartoon_name': '김용민의 그림마당',
        'url': 'https://www.khan.co.kr/cartoon',
        'enabled': True
    }
}

# 크롤링 설정
CRAWLING_CONFIG = {
    # 기본 수집 일수
    'default_days': 7,
    
    # 요청 간격 (초) - 서버 부하 방지
    'request_delay': 1,
    'site_delay': 2,
    
    # 타임아웃 설정 (초)
    'request_timeout': 15,
    'selenium_timeout': 10,
    
    # 재시도 설정
    'max_retries': 3,
    'retry_delay': 2,
    
    # User-Agent 설정
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 키워드 분석 설정
KEYWORD_CONFIG = {
    # 정치 관련 키워드
    'political_keywords': {
        '내란': ['내란', '정치', '대통령', '헌법'],
        '탄핵': ['탄핵', '정치', '대통령', '국회'],
        '대통령': ['대통령', '정치', '청와대'],
        '정부': ['정부', '정치', '행정'],
        '국회': ['국회', '정치', '의회'],
        '여당': ['여당', '정치', '집권'],
        '야당': ['야당', '정치', 'opposition'],
        '선거': ['선거', '정치', '투표'],
        '정당': ['정당', '정치', '당'],
        '의원': ['의원', '정치', '국회'],
        '장관': ['장관', '정치', '정부'],
        '청와대': ['청와대', '정치', '대통령'],
        '국정감사': ['국정감사', '정치', '국회'],
        '법안': ['법안', '정치', '입법'],
        '개헌': ['개헌', '정치', '헌법']
    },
    
    # 사회경제 키워드
    'social_economic_keywords': {
        '경제': ['경제', '금융', '시장'],
        '부동산': ['부동산', '경제', '주택'],
        '물가': ['물가', '경제', '인플레이션'],
        '환율': ['환율', '경제', '달러'],
        '증시': ['증시', '경제', '주식'],
        '금리': ['금리', '경제', '은행'],
        '일자리': ['일자리', '경제', '고용'],
        '최저임금': ['최저임금', '경제', '노동'],
        '교육': ['교육', '사회', '학교'],
        '의료': ['의료', '보건', '사회'],
        '환경': ['환경', '기후', '사회'],
        '복지': ['복지', '사회', '정책'],
        '노동': ['노동', '사회', '근로자'],
        '청년': ['청년', '사회', '세대'],
        '고령화': ['고령화', '사회', '인구']
    },
    
    # 국제 관계 키워드
    'international_keywords': {
        '북한': ['북한', '외교', '안보'],
        '중국': ['중국', '외교', '국제'],
        '일본': ['일본', '외교', '국제'],
        '미국': ['미국', '외교', '국제'],
        '러시아': ['러시아', '외교', '국제'],
        '한미': ['한미', '외교', '동맹'],
        '한중': ['한중', '외교', '관계'],
        '한일': ['한일', '외교', '관계'],
        '외교': ['외교', '국제', '관계'],
        '무역': ['무역', '경제', '국제'],
        '안보': ['안보', '군사', '국방']
    },
    
    # 사회 이슈 키워드
    'social_issues_keywords': {
        '코로나': ['코로나', '방역', '보건'],
        '백신': ['백신', '방역', '보건'],
        '마스크': ['마스크', '방역', '코로나'],
        '재난': ['재난', '안전', '사회'],
        '안전': ['안전', '사회', '생활'],
        '교통': ['교통', '사회', '인프라'],
        '통신': ['통신', '기술', '사회'],
        '인터넷': ['인터넷', '기술', 'IT'],
        'AI': ['AI', '기술', '인공지능'],
        '기후': ['기후', '환경', '온난화']
    }
}

# 신문사별 특성 키워드
NEWSPAPER_CHARACTERISTICS = {
    '오마이뉴스': ['시민', '참여', '개혁', '진보'],
    '한겨레': ['진보', '민주', '평화', '환경'],
    '경향신문': ['자유', '정의', '진실', '독립']
}

# 데이터 저장 설정
DATA_CONFIG = {
    # 저장 디렉토리
    'data_dir': 'data',
    
    # 파일 이름 형식
    'filename_format': 'cartoon_analysis_{timestamp}',
    
    # 저장할 파일 형식
    'save_formats': ['csv', 'json'],
    
    # CSV 인코딩
    'csv_encoding': 'utf-8-sig',
    
    # 최대 저장 파일 수 (오래된 파일 자동 삭제)
    'max_files': 10
}

# Selenium 설정
SELENIUM_CONFIG = {
    # Chrome 옵션
    'chrome_options': [
        '--headless',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--window-size=1920,1080',
        '--disable-blink-features=AutomationControlled',
        '--disable-extensions'
    ],
    
    # 암시적 대기 시간
    'implicit_wait': 10,
    
    # 페이지 로드 대기 시간
    'page_load_timeout': 30
}

# 대시보드 설정
DASHBOARD_CONFIG = {
    # 페이지 설정
    'page_title': '시사만평 분석 대시보드',
    'page_icon': '📰',
    'layout': 'wide',
    
    # 차트 색상 테마
    'color_schemes': {
        'primary': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
        'newspaper': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'],
        'keyword': 'Viridis'
    },
    
    # 표시할 최대 키워드 수
    'max_keywords_display': 15,
    
    # 갤러리 이미지 크기
    'gallery_image_width': 300,
    
    # 자동 새로고침 간격 (초)
    'auto_refresh_interval': 300
}

# 로깅 설정
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': 'cartoon_crawler.log',
    'max_log_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# 이미지 처리 설정 (OCR 사용 시)
IMAGE_CONFIG = {
    # OCR 언어 설정
    'ocr_languages': 'kor+eng',
    
    # 이미지 다운로드 타임아웃
    'download_timeout': 30,
    
    # 최대 이미지 크기 (바이트)
    'max_image_size': 5 * 1024 * 1024,  # 5MB
    
    # 지원하는 이미지 형식
    'supported_formats': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
}

# 에러 처리 설정
ERROR_CONFIG = {
    # 최대 연속 실패 횟수
    'max_consecutive_failures': 5,
    
    # 실패 시 대기 시간 (초)
    'failure_delay': 5,
    
    # 크리티컬 에러 시 중단 여부
    'stop_on_critical_error': False,
    
    # 에러 보고서 생성 여부
    'generate_error_report': True
}

# 개발자 설정
DEVELOPER_CONFIG = {
    'debug_mode': False,
    'verbose_logging': False,
    'save_raw_html': False,
    'performance_monitoring': False
}