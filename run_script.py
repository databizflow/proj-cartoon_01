#!/usr/bin/env python3
"""
시사만평 크롤링 & 대시보드 통합 실행 스크립트

초보자도 쉽게 사용할 수 있도록 만든 올인원 스크립트입니다.
"""

import sys
import subprocess
import os
from pathlib import Path
import time

def print_header():
    """헤더 출력"""
    print("=" * 60)
    print("📰 시사만평 크롤링 & 분석 대시보드")
    print("=" * 60)
    print("국내 주요 신문사 만평을 수집하고 분석합니다.")
    print("대상: 오마이뉴스, 한겨레, 경향신문")
    print("=" * 60)

def check_requirements():
    """필요한 패키지 설치 확인"""
    print("\n🔍 필요한 패키지 확인 중...")
    
    required_packages = [
        'requests', 'beautifulsoup4', 'selenium', 'pandas', 
        'streamlit', 'plotly', 'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 설치 필요")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  누락된 패키지: {', '.join(missing_packages)}")
        install = input("자동으로 설치하시겠습니까? (y/n): ")
        
        if install.lower() == 'y':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
                print("✅ 패키지 설치 완료!")
            except subprocess.CalledProcessError:
                print("❌ 패키지 설치 실패. 수동으로 설치해주세요:")
                print(f"pip install {' '.join(missing_packages)}")
                return False
        else:
            print("패키지를 먼저 설치해주세요.")
            return False
    
    return True

def run_crawler():
    """크롤러 실행"""
    print("\n🕷️  크롤링 시작...")
    
    try:
        from cartoon_crawler import CartoonCrawler
        
        # 사용자 입력
        print("\n설정:")
        try:
            days = int(input("수집할 날짜 수 (기본값 7): ") or "7")
        except ValueError:
            days = 7
            print("잘못된 입력. 기본값 7일로 설정합니다.")
        
        print(f"최근 {days}일간의 만평을 수집합니다...")
        
        # 크롤링 실행
        crawler = CartoonCrawler()
        results = crawler.crawl_all_sites(days=days)
        
        if results:
            df = crawler.save_results('cartoon_analysis')
            print(f"✅ 크롤링 완료! {len(results)}개 항목 수집")
            return True
        else:
            print("❌ 수집된 데이터가 없습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        return False

def run_dashboard():
    """대시보드 실행"""
    print("\n🎛️  대시보드 시작...")
    print("브라우저에서 http://localhost:8501 으로 접속하세요.")
    print("종료하려면 Ctrl+C를 누르세요.")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
    except KeyboardInterrupt:
        print("\n👋 대시보드를 종료합니다.")
    except Exception as e:
        print(f"❌ 대시보드 실행 오류: {e}")

def main():
    """메인 함수"""
    print_header()
    
    # 1. 패키지 확인
    if not check_requirements():
        return
    
    # 2. 사용자 선택
    while True:
        print("\n📋 메뉴를 선택하세요:")
        print("1. 만평 데이터 크롤링")
        print("2. 대시보드 실행")
        print("3. 크롤링 + 대시보드 (전체 실행)")
        print("4. 종료")
        
        choice = input("\n선택 (1-4): ").strip()
        
        if choice == '1':
            run_crawler()
            
        elif choice == '2':
            # 데이터 파일 존재 확인
            data_dir = Path("data")
            csv_files = list(data_dir.glob("cartoon_analysis_*.csv")) if data_dir.exists() else []
            
            if not csv_files:
                print("⚠️  데이터 파일이 없습니다. 먼저 크롤링을 실행하세요.")
                continue
                
            run_dashboard()
            
        elif choice == '3':
            # 전체 실행
            success = run_crawler()
            if success:
                print("\n잠시 후 대시보드를 시작합니다...")
                time.sleep(3)
                run_dashboard()
            
        elif choice == '4':
            print("👋 프로그램을 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다. 1-4 중에서 선택해주세요.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 사용자에 의해 프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        print("문제가 지속되면 개발자에게 문의해주세요.")