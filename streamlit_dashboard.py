import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import re
from collections import Counter
import time
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(
    page_title="시사만평 분석 대시보드",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 50%, #f8f9fa 100%);
        padding: 15px 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 20px 0;
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #1f77b4;
    }
    .newspaper-tag {
        display: inline-block;
        padding: 0.25em 0.5em;
        margin: 0.1em;
        background-color: #e1ecf4;
        color: #0066cc;
        border-radius: 0.25rem;
        font-size: 0.85em;
    }
    .keyword-tag {
        display: inline-block;
        padding: 0.2em 0.4em;
        margin: 0.1em;
        background-color: #fff2cc;
        color: #b07c00;
        border-radius: 0.2rem;
        font-size: 0.8em;
    }
    .sub-header {
        background: transparent;
        padding: 8px 0;
        border-bottom: 2px solid #e9ecef;
        margin: 20px 0 15px 0;
        font-size: 1.2rem;
        font-weight: 600;
        color: #495057;
        position: relative;
    }
    .sub-header::after {
        content: "";
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background: #6c757d;
    }
    .date-header {
        background: #f8f9fa;
        border: 2px solid #dee2e6;
        padding: 8px 20px;
        border-radius: 5px;
        margin: 20px 0 15px 0;
        font-size: 1rem;
        font-weight: 600;
        color: #495057;
        text-align: left;
        box-shadow: none;
        display: block;
        position: relative;
    }
    .date-header::before {
        content: "📅";
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

class CartoonDashboard:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
    def load_data(self):
        """데이터 로드"""
        csv_files = list(self.data_dir.glob("cartoon_data.csv"))
        if not csv_files:
            return None
        
        # 고정 파일 로드
        if csv_files:
            latest_file = csv_files[0]  # cartoon_data.csv
            df = pd.read_csv(latest_file, encoding='utf-8-sig')
        else:
            return None
        
        # 데이터 전처리
        df['date'] = pd.to_datetime(df['date'])
        df['keywords_list'] = df['keywords'].fillna('').apply(lambda x: [k.strip() for k in x.split(',') if k.strip()])
        
        return df, latest_file.name
    
    def display_summary_stats(self, df):
        """요약 통계 표시"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📰 총 만평 수",
                value=len(df),
                delta=f"최근 {(df['date'].max() - df['date'].min()).days + 1}일"
            )
        
        with col2:
            st.metric(
                label="🏢 신문사 수",
                value=df['newspaper'].nunique(),
                delta=", ".join(df['newspaper'].unique())
            )
        
        with col3:
            latest_date = df['date'].max().strftime('%Y-%m-%d')
            st.metric(
                label="📅 최신 데이터",
                value=latest_date,
                delta="오늘" if latest_date == datetime.now().strftime('%Y-%m-%d') else ""
            )
        
        with col4:
            image_count = df['image_url'].notna().sum()
            st.metric(
                label="🖼️ 이미지 수집률",
                value=f"{image_count}/{len(df)}",
                delta=f"{image_count/len(df)*100:.1f}%"
            )
    
    def create_keyword_wordcloud(self, df, period_days=30, selected_newspaper="전체"):
        """신문사별 선택 가능한 키워드 워드클라우드 생성"""
        # 기간 필터링
        if period_days == -1:  # 전체
            filtered_df = df
            period_text = "전체 기간"
        else:
            end_date = df['date'].max()
            start_date = end_date - timedelta(days=period_days-1)
            filtered_df = df[df['date'] >= start_date]
            period_text = f"최근 {period_days}일"
        
        # 신문사 필터링
        if selected_newspaper != "전체":
            filtered_df = filtered_df[filtered_df['newspaper'] == selected_newspaper]
            newspaper_text = f" - {selected_newspaper}"
        else:
            newspaper_text = " - 전체 신문사"
        
        # 키워드 수집
        all_keywords = []
        for keywords_list in filtered_df['keywords_list']:
            all_keywords.extend(keywords_list)
        
        if not all_keywords:
            return None, period_text
        
        # 키워드 빈도 계산
        keyword_counts = Counter(all_keywords)
        
        # 너무 일반적인 키워드 제외
        exclude_words = {'정치', '사회', '경제', '시민', '언론', '진보'}
        filtered_counts = {k: v for k, v in keyword_counts.items() 
                          if k not in exclude_words and len(k) > 1}
        
        if not filtered_counts:
            return None, period_text
        
        # 워드클라우드 생성
        try:
            # Windows 한글 폰트 경로들 시도
            font_paths = [
                'C:/Windows/Fonts/malgun.ttf',  # 맑은 고딕
                'C:/Windows/Fonts/gulim.ttc',   # 굴림
                'C:/Windows/Fonts/batang.ttc',  # 바탕
                'C:/Windows/Fonts/NanumGothic.ttf'  # 나눔고딕 (설치된 경우)
            ]
            
            font_path = None
            for path in font_paths:
                try:
                    import os
                    if os.path.exists(path):
                        font_path = path
                        break
                except:
                    continue
            
            if font_path:
                wordcloud = WordCloud(
                    font_path=font_path,
                    width=800, 
                    height=400,
                    background_color='white',
                    max_words=50,
                    colormap='viridis'
                ).generate_from_frequencies(filtered_counts)
            else:
                # 폰트를 찾을 수 없으면 기본 설정
                wordcloud = WordCloud(
                    width=800, 
                    height=400,
                    background_color='white',
                    max_words=50,
                    colormap='viridis'
                ).generate_from_frequencies(filtered_counts)
            
            # matplotlib 그래프로 변환 (한글 폰트 설정)
            plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(f'주요 키워드 워드클라우드 ({period_text}{newspaper_text})', fontsize=16, pad=20)
            
            return fig, period_text
            
        except Exception as e:
            # 모든 폰트 설정 실패 시 영어로 표시
            try:
                wordcloud = WordCloud(
                    width=800, 
                    height=400,
                    background_color='white',
                    max_words=50,
                    colormap='viridis'
                ).generate_from_frequencies(filtered_counts)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title(f'Keywords WordCloud ({period_text})', fontsize=16, pad=20)
                
                return fig, period_text
            except:
                return None, period_text
    

    
    def create_keyword_analysis(self, df):
        """키워드 분석"""
        all_keywords = []
        for keywords_list in df['keywords_list']:
            all_keywords.extend(keywords_list)
        
        keyword_counts = Counter(all_keywords)
        top_keywords = dict(keyword_counts.most_common(15))
        
        if top_keywords:
            fig = px.bar(
                x=list(top_keywords.values()),
                y=list(top_keywords.keys()),
                orientation='h',
                title="주요 키워드 TOP 15",
                labels={'x': '언급 횟수', 'y': '키워드'},
                color=list(top_keywords.values()),
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            return fig
        return None
    
    def create_enhanced_heatmap(self, df):
        """개선된 신문사별 날짜별 히트맵 (색상 구분 + 요일 정보)"""
        if df.empty:
            return None
        
        # 신문사 색상 (갤러리와 동일)
        newspaper_colors = {
            '오마이뉴스': '#1f77b4',
            '한겨레': '#ff7f0e', 
            '경향신문': '#2ca02c'
        }
        
        # 날짜 범위 생성
        date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
        newspapers = ['오마이뉴스', '한겨레', '경향신문']
        
        # 각 신문사별로 서브플롯 생성
        fig = go.Figure()
        
        for i, newspaper in enumerate(newspapers):
            newspaper_data = df[df['newspaper'] == newspaper]
            
            # 날짜별 만평 수 계산
            daily_counts = newspaper_data.groupby(newspaper_data['date'].dt.date).size()
            
            # 모든 날짜에 대해 데이터 준비
            y_values = []
            colors = []
            hover_texts = []
            
            for date in date_range:
                date_only = date.date()
                count = daily_counts.get(date_only, 0)
                
                # 요일 정보
                weekday_kr = ['월', '화', '수', '목', '금', '토', '일'][date.weekday()]
                
                y_values.append(count)
                colors.append(count)
                
                hover_text = f"{newspaper}<br>{date.strftime('%Y-%m-%d')} ({weekday_kr})<br>만평 수: {count}개"
                hover_texts.append(hover_text)
            
            # 각 신문사별 히트맵 추가 (원 안에 요일 표시)
            fig.add_trace(go.Scatter(
                x=date_range,
                y=[newspaper] * len(date_range),
                mode='markers+text',
                marker=dict(
                    size=[max(20, count * 25) for count in y_values],  # 크기 증가 (텍스트 공간)
                    color=y_values,
                    colorscale=[[0, 'white'], [1, newspaper_colors[newspaper]]],
                    showscale=False,
                    line=dict(width=2, color='gray'),
                    opacity=0.8
                ),
                text=[['월', '화', '수', '목', '금', '토', '일'][date.weekday()] if count > 0 else '' 
                      for date, count in zip(date_range, y_values)],
                textfont=dict(
                    size=10,
                    color='black' if newspaper in ['한겨레', '경향신문'] else 'white',  # 밝은 색 배경에는 검은 글씨
                    family='Arial Black'
                ),
                textposition='middle center',
                customdata=hover_texts,
                hovertemplate='%{customdata}<extra></extra>',
                name=newspaper
            ))
        
        # 레이아웃 설정
        fig.update_layout(
            title="신문사별 일별 발행 현황 (색상별 구분 + 요일 정보)",
            xaxis_title="날짜",
            yaxis_title="신문사",
            height=400,
            showlegend=False,
            xaxis=dict(
                tickangle=-45,
                tickformat='%m/%d',
                dtick=86400000.0 * 2  # 2일 간격으로 표시
            ),
            yaxis=dict(
                categoryorder='array',
                categoryarray=newspapers
            ),
            hovermode='closest'
        )
        
        # 요일별 배경색 추가 (주말 강조)
        for date in date_range:
            if date.weekday() == 5:  # 토요일
                fig.add_vrect(
                    x0=date - pd.Timedelta(hours=12),
                    x1=date + pd.Timedelta(hours=12),
                    fillcolor="lightyellow",
                    opacity=0.3,
                    layer="below",
                    line_width=0
                )
            elif date.weekday() == 6:  # 일요일
                fig.add_vrect(
                    x0=date - pd.Timedelta(hours=12),
                    x1=date + pd.Timedelta(hours=12),
                    fillcolor="lightcoral",
                    opacity=0.2,
                    layer="below",
                    line_width=0
                )
        
        return fig
    
    def display_cartoon_gallery_timeline(self, df):
        """타임라인 형태 만평 갤러리 (기간 선택 + 동적 컬럼)"""
        
        # 기간 선택 옵션
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            # 빠른 선택 버튼들
            period_options = {
                "최근 3일": 3,
                "최근 7일": 7, 
                "최근 14일": 14,
                "최근 30일": 30
            }
            
            selected_period = st.selectbox("기간 선택", list(period_options.keys()), index=1)
            days = period_options[selected_period]
            
            # 기간 계산 (데이터가 없을 때 기본값 사용)
            if not df.empty:
                end_date = df['date'].max().date()
                start_date = end_date - timedelta(days=days-1)
                min_date = df['date'].min().date()
                max_date = df['date'].max().date()
                
                # start_date가 min_date보다 작으면 min_date로 조정
                if start_date < min_date:
                    start_date = min_date
            else:
                # 데이터가 없을 때 기본값
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days-1)
                min_date = start_date  # min_date를 start_date와 같게 설정
                max_date = end_date
        
        with col2:
            # 커스텀 시작일
            custom_start = st.date_input(
                "시작일 (커스텀)",
                value=start_date,
                min_value=min_date,
                max_value=max_date
            )
        
        with col3:
            # 커스텀 종료일  
            custom_end = st.date_input(
                "종료일 (커스텀)",
                value=end_date,
                min_value=min_date,
                max_value=max_date
            )
        
        # 커스텀 날짜가 변경되었으면 그것을 사용
        if custom_start != start_date or custom_end != end_date:
            start_date = custom_start
            end_date = custom_end
        
        # 기간 데이터 필터링
        filtered_df = df[
            (df['date'].dt.date >= start_date) & 
            (df['date'].dt.date <= end_date)
        ].sort_values('date', ascending=False)
        
        if filtered_df.empty:
            st.warning("선택한 기간에 만평이 없습니다.")
            return
        
        st.info(f"📊 {start_date} ~ {end_date} 기간의 만평 {len(filtered_df)}개")
        
        # 신문사 색상 정의
        newspaper_colors = {
            '오마이뉴스': '#1f77b4',
            '한겨레': '#ff7f0e', 
            '경향신문': '#2ca02c'
        }
        
        # 날짜별로 그룹화 (최신 날짜부터)
        dates_sorted = sorted(filtered_df['date'].dt.date.unique(), reverse=True)
        for date in dates_sorted:
            day_data = filtered_df[filtered_df['date'].dt.date == date]
            st.markdown(f'<div class="date-header">{date.strftime("%Y년 %m월 %d일")} ({["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"][date.weekday()]})</div>', unsafe_allow_html=True)
            
            # 신문사 순서 고정 (오마이뉴스 → 한겨레 → 경향신문)
            newspaper_order = ['오마이뉴스', '한겨레', '경향신문']
            available_cartoons = []
            
            for newspaper in newspaper_order:
                newspaper_data = day_data[day_data['newspaper'] == newspaper]
                if not newspaper_data.empty:
                    available_cartoons.extend(newspaper_data.to_dict('records'))
            num_cartoons = len(available_cartoons)
            
            if num_cartoons == 0:
                continue
            elif num_cartoons == 1:
                cols = st.columns([1])
            elif num_cartoons == 2:
                cols = st.columns([1, 1])
            else:  # 3개 이상
                cols = st.columns([1, 1, 1])
            
            # 각 만평을 카드 형태로 표시
            for i, cartoon in enumerate(available_cartoons):
                col_idx = i % len(cols)  # 컬럼 순환
                
                with cols[col_idx]:
                    # 신문사별 카드 스타일
                    newspaper = cartoon['newspaper']
                    color = newspaper_colors.get(newspaper, '#666666')
                    
                    # 카드 컨테이너
                    with st.container():
                        # 신문사 태그
                        st.markdown(f"""
                        <div style="
                            background: {color};
                            color: white;
                            padding: 5px 10px;
                            border-radius: 15px;
                            text-align: center;
                            font-size: 14px;
                            font-weight: bold;
                            margin-bottom: 10px;
                        ">
                            📰 {newspaper}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 이미지 (고정 높이)
                        if cartoon['image_url'] and pd.notna(cartoon['image_url']):
                            try:
                                st.image(
                                    cartoon['image_url'], 
                                    width=None,
                                    caption=None
                                )
                            except:
                                st.error("이미지 로드 실패")
                        else:
                            st.info("이미지 없음")
                        
                        # 제목
                        st.markdown(f"**{cartoon['title']}**")
                        
                        # 키워드 (최대 3개)
                        if cartoon['keywords']:
                            keywords_html = ""
                            for keyword in cartoon['keywords'].split(',')[:3]:
                                keyword = keyword.strip()
                                if keyword:
                                    keywords_html += f'<span class="keyword-tag">{keyword}</span> '
                            st.markdown(keywords_html, unsafe_allow_html=True)
                        
                        # 원문 링크
                        if cartoon['source_url']:
                            st.markdown(f"[📖 원문]({cartoon['source_url']})")
            

    
    def display_data_table(self, df):
        """데이터 테이블"""
        
        # 검색 기능
        search_term = st.text_input("제목 또는 키워드로 검색")
        
        display_df = df[['newspaper', 'date', 'title', 'keywords', 'source_url']].copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        
        if search_term:
            mask = (
                display_df['title'].str.contains(search_term, case=False, na=False) |
                display_df['keywords'].str.contains(search_term, case=False, na=False)
            )
            display_df = display_df[mask]
        
        st.dataframe(
            display_df,
            column_config={
                "newspaper": "신문사",
                "date": "날짜",
                "title": "제목",
                "keywords": "키워드",
                "source_url": st.column_config.LinkColumn("원문 링크")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # 다운로드 버튼
        csv = display_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="CSV 다운로드",
            data=csv,
            file_name=f"cartoon_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    def run_dashboard(self):
        """대시보드 실행"""
        # 헤더
        st.markdown('<h1 class="main-header">📰 시사만평 분석 대시보드</h1>', unsafe_allow_html=True)
        
        # 제목 아래 간격 추가
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # 데이터 로드
        data_result = self.load_data()
        if data_result is None:
            st.error("데이터 파일을 찾을 수 없습니다. 먼저 크롤링을 실행해주세요.")
            st.code("python cartoon_crawler.py")
            return
        
        df, filename = data_result
        
        # 사이드바
        with st.sidebar:
            st.markdown("### 대시보드 정보")
            st.info(f"**데이터 파일:** {filename}")
            st.markdown(f"""
            <div style="
                background-color: #d1ecf1;
                border: 1px solid #bee5eb;
                border-radius: 0.25rem;
                padding: 0.75rem;
                margin-bottom: 1rem;
                color: #0c5460;
            ">
                <strong>마지막 업데이트:</strong><br>
                {datetime.now().strftime('%Y-%m-%d')}
                {datetime.now().strftime('%H:%M:%S')}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("데이터 새로고침"):
                st.rerun()
            
            st.markdown("### 분석 옵션")
            show_gallery = st.checkbox("만평 갤러리 표시", value=True)
            show_data_table = st.checkbox("전체 데이터 목록 보기", value=False)
        
        # 메인 대시보드
        # 1. 요약 통계
        st.markdown('<div class="section-header">요약 통계</div>', unsafe_allow_html=True)
        self.display_summary_stats(df)
        
        # 제목과 통계 사이 간격 추가
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. 차트 섹션
        st.markdown('<div class="section-header">데이터 시각화</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 두 번째 행: 신문사별 워드클라우드 (전체 너비)
        st.markdown('<div class="sub-header">신문사별 키워드 분석</div>', unsafe_allow_html=True)
        
        # 신문사와 기간 선택
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            newspaper_options = ["전체", "오마이뉴스", "한겨레"]
            selected_newspaper = st.selectbox("신문사 선택", newspaper_options, index=0)
        
        with col2:
            period_options = {
                "최근 7일": 7,
                "최근 30일": 30,
                "전체 기간": -1
            }
            selected_period = st.selectbox("분석 기간", list(period_options.keys()), index=1)
            period_days = period_options[selected_period]
        
        # 워드클라우드 생성 및 표시
        wordcloud_fig, period_text = self.create_keyword_wordcloud(df, period_days, selected_newspaper)
        if wordcloud_fig:
            st.pyplot(wordcloud_fig)
            
            # 설명 추가
            if selected_newspaper == "전체":
                st.info("💡 전체 신문사의 키워드를 종합 분석한 결과입니다.")
            else:
                st.info(f"💡 {selected_newspaper}의 키워드 분석 결과입니다. (경향신문은 제목 정보 부족으로 제외)")
        else:
            st.warning(f"{selected_newspaper}의 {period_text} 동안 분석할 키워드가 충분하지 않습니다.")
        
        # 세 번째 행: 개선된 히트맵 (전체 너비)
        st.markdown("<br>", unsafe_allow_html=True)
        enhanced_heatmap = self.create_enhanced_heatmap(df)
        if enhanced_heatmap:
            st.plotly_chart(enhanced_heatmap, use_container_width=True)
            
            # 히트맵 설명 추가
            st.markdown("""
            **📊 히트맵 해석 가이드:**
            - 🔵 **오마이뉴스** (파란색) | 🟠 **한겨레** (주황색) | 🟢 **경향신문** (초록색)
            - **원의 크기**: 해당 날짜의 만평 개수 (클수록 많음)
            - **회색 배경**: 주말 (토요일, 일요일)
            - **마우스 오버**: 상세 정보 (날짜, 요일, 만평 수) 확인 가능
            """)
        else:
            st.info("히트맵을 생성할 데이터가 부족합니다.")
        
        st.divider()
        
        # 3. 만평 갤러리 (타임라인 구성)
        if show_gallery:
            st.markdown('<div class="section-header">만평 갤러리</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            self.display_cartoon_gallery_timeline(df)
            st.divider()
        
        # 4. 데이터 테이블
        if show_data_table:
            st.markdown('<div class="section-header">전체 데이터</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            self.display_data_table(df)

# 메인 실행
def main():
    dashboard = CartoonDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()