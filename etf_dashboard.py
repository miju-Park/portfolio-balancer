import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from datetime import datetime

class PortfolioDashboard:
    def __init__(self, db_name='investment_portfolio.db'):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """각 투자 유형별 데이터베이스 테이블 초기화"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # 개인연금 테이블
        c.execute('''
            CREATE TABLE IF NOT EXISTS personal_pension (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                total_value REAL,
                deposit REAL
            )
        ''')
        
        # 퇴직연금 테이블
        c.execute('''
            CREATE TABLE IF NOT EXISTS retirement_pension (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                total_value REAL,
                deposit REAL
            )
        ''')
        
        # 코인 테이블
        c.execute('''
            CREATE TABLE IF NOT EXISTS cryptocurrency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                total_value REAL,
                deposit REAL
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_portfolio_history(self, portfolio_type, total_value, deposit):
        """포트폴리오 히스토리 저장"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        table_name = {
            '개인연금': 'personal_pension',
            '퇴직연금': 'retirement_pension',
            '코인': 'cryptocurrency'
        }.get(portfolio_type)
        
        c.execute(f"INSERT INTO {table_name} (date, total_value, deposit) VALUES (?, ?, ?)", 
                  (current_date, total_value, deposit))
        conn.commit()
        conn.close()

    def get_portfolio_history(self, portfolio_type):
        """포트폴리오 히스토리 불러오기"""
        conn = sqlite3.connect(self.db_name)
        table_name = {
            '개인연금': 'personal_pension',
            '퇴직연금': 'retirement_pension',
            '코인': 'cryptocurrency'
        }.get(portfolio_type)
        
        history_df = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY date", conn)
        conn.close()
        
        return history_df

def calculate_rebalancing(etfs, total_deposit):
    """기존 리밸런싱 함수와 동일"""
    total_portfolio_value = sum(etf['current_price'] * etf['current_qty'] for etf in etfs)
    total_investment = total_portfolio_value + total_deposit

    etf_values = []
    for etf in etfs:
        current_value = etf['current_price'] * etf['current_qty']
        current_ratio = current_value / total_investment
        target_value = total_investment * etf['target_ratio']
        etf_values.append({
            'etf': etf,
            'current_value': current_value,
            'current_ratio': current_ratio,
            'target_value': target_value,
            'target_ratio': etf['target_ratio'],
            'value_difference': target_value - current_value
        })

    sorted_etfs = sorted(etf_values, key=lambda x: abs(x['value_difference']), reverse=True)

    rebalancing_results = []
    remaining_deposit = total_deposit
    for item in sorted_etfs:
        etf = item['etf']
        value_difference = item['value_difference']
        
        trade_value = value_difference if abs(value_difference) <= remaining_deposit else (remaining_deposit if value_difference > 0 else -remaining_deposit)
        
        qty_to_trade = int(trade_value / etf['current_price'])
        
        remaining_deposit -= abs(qty_to_trade * etf['current_price'])
        
        result = {
            'name': etf['name'],
            'current_qty': etf['current_qty'],
            'current_price': etf['current_price'],
            'current_value': item['current_value'],
            'current_ratio': item['current_ratio'],
            'target_ratio': item['target_ratio'],
            'qty_to_trade': qty_to_trade,
            'trade_type': '매수' if qty_to_trade > 0 else '매도' if qty_to_trade < 0 else '유지'
        }
        rebalancing_results.append(result)

    return rebalancing_results, sum(etf['current_price'] * etf['current_qty'] for etf in etfs)

def main():
    st.set_page_config(layout="wide", page_title="투자 포트폴리오 대시보드")
    portfolio_dashboard = PortfolioDashboard()

    # 기본 ETF 설정들
    default_etfs = {
        '개인연금': [
            {'name': 'KOSPI200 ETF', 'current_price': 50000, 'current_qty': 10, 'target_ratio': 0.3},
            {'name': '나스닥 ETF', 'current_price': 75000, 'current_qty': 5, 'target_ratio': 0.2},
            {'name': '채권 ETF', 'current_price': 40000, 'current_qty': 8, 'target_ratio': 0.2},
            {'name': '글로벌 ETF', 'current_price': 60000, 'current_qty': 6, 'target_ratio': 0.15},
            {'name': '부동산 ETF', 'current_price': 45000, 'current_qty': 7, 'target_ratio': 0.15}
        ],
        '퇴직연금': [
            {'name': '국내대형주 ETF', 'current_price': 55000, 'current_qty': 8, 'target_ratio': 0.4},
            {'name': '채권 ETF', 'current_price': 42000, 'current_qty': 10, 'target_ratio': 0.3},
            {'name': '해외주식 ETF', 'current_price': 65000, 'current_qty': 5, 'target_ratio': 0.2},
            {'name': '중소형주 ETF', 'current_price': 48000, 'current_qty': 6, 'target_ratio': 0.1}
        ],
        '코인': [
            {'name': 'Bitcoin', 'current_price': 60000000, 'current_qty': 0.1, 'target_ratio': 0.5},
            {'name': 'Ethereum', 'current_price': 4000000, 'current_qty': 2, 'target_ratio': 0.3},
            {'name': 'Others', 'current_price': 1000000, 'current_qty': 5, 'target_ratio': 0.2}
        ]
    }

    st.title('🚀 투자 포트폴리오 대시보드')

    # 탭 생성
    tab1, tab2, tab3 = st.tabs(['🏦 개인연금', '💼 퇴직연금', '💰 코인'])

    def create_portfolio_tab(tab, portfolio_type):
        with tab:
            col1, col2 = st.columns([3, 1])

            with col2:
                total_deposit = st.number_input(f'{portfolio_type} 예수금', value=1000000, step=100000)
                
                if st.button(f'{portfolio_type} 리밸런싱 실행'):
                    # 리밸런싱 수행
                    results, current_portfolio_value = calculate_rebalancing(default_etfs[portfolio_type], total_deposit)
                    
                    # 포트폴리오 기록 저장
                    portfolio_dashboard.save_portfolio_history(portfolio_type, current_portfolio_value + total_deposit, total_deposit)
                    
                    # 결과 표시
                    results_df = pd.DataFrame(results)
                    
                    with col1:
                        st.subheader(f'{portfolio_type} 리밸런싱 결과')
                        st.dataframe(
                            results_df[['name', 'current_value', 'current_qty', 'current_ratio', 'target_ratio', 'qty_to_trade']].style.format({
                                'current_value': '{:,.0f}원',
                                'current_ratio': '{:.2%}',
                                'target_ratio': '{:.2%}',
                                'qty_to_trade': '{:,.0f}'
                            }),
                            use_container_width=True
                        )

            with col1:
                # 포트폴리오 히스토리 그래프
                st.subheader(f'{portfolio_type} 누적 가치 히스토리')
                
                history_df = portfolio_dashboard.get_portfolio_history(portfolio_type)
                
                if not history_df.empty:
                    history_df['date'] = pd.to_datetime(history_df['date'])
                    fig = px.line(history_df, x='date', y='total_value', 
                                  title=f'{portfolio_type} 총 가치 추이',
                                  labels={'total_value': '총 가치', 'date': '날짜'},
                                  hover_data={'deposit': ':.0f원', 'total_value': ':.0f원'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("아직 포트폴리오 기록이 없습니다.")

    # 각 탭에 대한 포트폴리오 대시보드 생성
    create_portfolio_tab(tab1, '개인연금')
    create_portfolio_tab(tab2, '퇴직연금')
    create_portfolio_tab(tab3, '코인')

if __name__ == "__main__":
    main()