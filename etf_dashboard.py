import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from utils import get_month_format

class PortfolioInfo:
    def __init__(self, db_name='portfolio_info.db'):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """각 투자 유형별 데이터베이스 테이블 초기화"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # 개인연금 테이블
        c.execute('''
            CREATE TABLE IF NOT EXISTS personal_pension_info (
                code TEXT PRIMARY KEY,
                name TEXT,
                current_qty INTEGER,
                current_price INTEGER,
                target_ratio REAL
            )
        ''')
        
        # 퇴직연금 테이블
        c.execute('''
            CREATE TABLE IF NOT EXISTS retirement_pension_info (
                code TEXT PRIMARY KEY,
                name TEXT,
                current_qty INTEGER,
                current_price INTEGER,
                target_ratio REAL
            )
        ''')
        
        # 코인 테이블 TBD
        # c.execute('''
        #     CREATE TABLE IF NOT EXISTS cryptocurrency (
        #         date TEXT PRIMARY KEY,
        #         total_value REAL
        #     )
        # ''')

        # 삽입할 데이터
        data = [
            {'name':'TIGER 미국S&P500선물', "code":'143850',"current_price":64580, "current_qty":262, "target_ratio":0.25},
            {'name':'KODEX 골드선물', "code":'132030',"current_price":15970, "current_qty":424, "target_ratio":0.1},
            {'name':'TIGER 단기통안채', "code":'157450',"current_price":109150, "current_qty":80, "target_ratio":0.13},
            {'name':'KODEX 국채선물 10년', "code":'152380',"current_price":69450, "current_qty":125, "target_ratio":0.13},
            {'name':'신흥국 MSCI', "code":'195980',"current_price":9780, "current_qty":1667, "target_ratio":0.25},
            {'name':'KODEX 미국10년국채선물', "code":'308620',"current_price":11890, "current_qty":752, "target_ratio":0.13}
        ]

        pension_data= [
            {'name':'TIGER 미국S&P500', "code":'36075',"current_price":21260,
                "current_qty":115, "target_ratio":0.25},
            {'name':'ACE KRX금현물', "code":'411060',"current_price":17160,
                "current_qty":125, "target_ratio":0.25},
            {'name':'KOSEF 국고채10년', "code":'148070',"current_price":119350,
                "current_qty":29, "target_ratio":0.25},
            {'name':'KODEX 200 미국채혼합', "code":'284430',"current_price":12740,
                "current_qty":420, "target_ratio":0.25},
            {'name':'KOSEF 200 TR', "code":'294400',"current_price":41735,
                "current_qty":3, "target_ratio":0.25}
        ]

        # 데이터 삽입 또는 업데이트
        for item in data:
            c.execute('''
                INSERT OR REPLACE INTO personal_pension_info (code, name, current_price, current_qty, target_ratio)
                VALUES (:code, :name, :current_price, :current_qty, :target_ratio)
            ''', item)

        for item in pension_data:
            c.execute('''
                INSERT OR REPLACE INTO retirement_pension_info (code, name, current_price, current_qty, target_ratio)
                VALUES (:code, :name, :current_price, :current_qty, :target_ratio)
            ''', item)

        
        conn.commit()
        conn.close()
    
    def update_portfolio_info(self, portfolio_type, data):
        """포트폴리오 히스토리 저장"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        table_name = {
            '개인연금': 'personal_pension_info',
            '퇴직연금': 'retirement_pension_info',
            '코인': ''
        }.get(portfolio_type)
    
        query = f'''
        INSERT OR REPLACE INTO {table_name} (code, name, current_price, current_qty, target_ratio)
    VALUES (:code, :name, :current_price, :current_qty, :target_ratio)
        '''
        for item in data:
            c.execute(query,item)
        conn.commit()
        conn.close()
    
    def get_portfolio_info(self, portfolio_type):
        """포트폴리오 히스토리 불러오기"""
        conn = sqlite3.connect(self.db_name)
        table_name = {
            '개인연금': 'personal_pension_info',
            '퇴직연금': 'retirement_pension_info',
            '코인': 'cryptocurrency'
        }.get(portfolio_type)


        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # 컬럼 이름 정의
        column_names = ['code', 'name', 'current_qty', 'current_price', 'target_ratio']

        # 데이터를 딕셔너리 리스트로 변환
        data_list = [dict(zip(column_names,row)) for row in rows]

        conn.close()
        
        return data_list

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
                date TEXT PRIMARY KEY,
                total_value REAL
            )
        ''')
        
        # 퇴직연금 테이블
        c.execute('''
            CREATE TABLE IF NOT EXISTS retirement_pension (
                date TEXT PRIMARY KEY,
                total_value REAL
            )
        ''')
        
        # 코인 테이블
        c.execute('''
            CREATE TABLE IF NOT EXISTS cryptocurrency (
                date TEXT PRIMARY KEY,
                total_value REAL
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_portfolio_history(self, portfolio_type, total_value):
        """포트폴리오 히스토리 저장"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        current_date = get_month_format()
        
        table_name = {
            '개인연금': 'personal_pension',
            '퇴직연금': 'retirement_pension',
            '코인': 'cryptocurrency'
        }.get(portfolio_type)
    
        query = f'''
        INSERT INTO {table_name} (date, total_value) 
        VALUES (?, ?) 
        ON CONFLICT(date) DO UPDATE SET 
        total_value = excluded.total_value
        '''
        
        c.execute(query,(current_date, total_value))
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
def convert_to_number(input_value):
    # 이미 숫자인 경우 그대로 반환
    if isinstance(input_value, (int, float)):
        return input_value
    
    # 문자열인 경우 변환
    if isinstance(input_value, str):
        # 콤마와 통화 기호 제거
        cleaned_str = input_value.replace(',', '').replace('₩', '').strip()
        
        try:
            # 정수로 변환 시도
            return int(cleaned_str)
        except ValueError:
            try:
                # 실수로 변환 시도
                return float(cleaned_str)
            except ValueError:
                # 변환 실패 시 None 반환
                return None
    
    # 다른 타입의 경우 None 반환
    return None

def calculate_current_ratio(info):
    # Calculate total current value
    total_current_value = sum(item['current_price'] * item['current_qty'] for item in info)
    
    # Add current_ratio to each item
    for item in info:
        current_value = (item['current_price'] * item['current_qty'])/ total_current_value
        item['current_value'] = current_value
    
    return info

def prepare_portfolio_dataframe(info):
    # Calculate current ratios
    info_with_ratio = calculate_current_ratio(info)
    
    # Convert to DataFrame
    df = pd.DataFrame(info_with_ratio)
    
    # Calculate additional columns for rebalancing
    df['current_value'] = df['current_price'] * df['current_qty']
    df['qty_to_trade'] = 0  # Placeholder, will be calculated during rebalancing
    
    return df

def calculate_rebalancing(etfs, total_deposit):
    
    total_portfolio_value = sum(convert_to_number(etf['current_price']) * convert_to_number(etf['current_qty']) for etf in etfs)
    total_investment = total_portfolio_value + total_deposit

    etf_values = []
    for etf in etfs:
        current_value = int(etf['current_price']) * int(etf['current_qty'])
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
    portfolio_update_info = []
    remaining_deposit = total_deposit
    for item in sorted_etfs:
        etf = item['etf']
        value_difference = item['value_difference']
        
        trade_value = value_difference if abs(value_difference) <= remaining_deposit else (remaining_deposit if value_difference > 0 else -remaining_deposit)
        
        qty_to_trade = int(trade_value / etf['current_price'])
        
        remaining_deposit -= abs(qty_to_trade * etf['current_price'])
        
        result = {
            'name': etf['name'],
            'current_price': etf['current_price'],
            'current_qty': etf['current_qty'],
            'current_value': item['current_value'],
            'current_ratio': item['current_ratio'],
            'target_ratio': item['target_ratio'],
            'qty_to_trade': qty_to_trade,
            'trade_type': '매수' if qty_to_trade > 0 else '매도' if qty_to_trade < 0 else '유지'
        }
        rebalancing_results.append(result)
        
        portfolio_update_info.append({
            'name': etf['name'],
            'code': etf['code'],
            'current_price': etf['current_price'],
            'current_qty': etf['current_qty']+ qty_to_trade,
            'current_value': item['current_value'],
            'current_ratio': item['current_ratio'],
            'target_ratio': item['target_ratio'],
        })
        

    return rebalancing_results, sum(etf['current_price'] * etf['current_qty'] for etf in etfs), portfolio_update_info

def main():
    st.set_page_config(layout="wide", page_title="투자 포트폴리오 대시보드")
    portfolio_dashboard = PortfolioDashboard()
    portfolio_info = PortfolioInfo()

    # 기본 ETF 설정들
    default_etfs = {
        '개인연금': portfolio_info.get_portfolio_info('개인연금'),
        '퇴직연금': portfolio_info.get_portfolio_info('퇴직연금'),
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
        # Deposit input
        total_deposit = st.number_input(f'{portfolio_type} 예수금', value=1000000, step=100000)
    
        # Create an editable dataframe
        etf_data = prepare_portfolio_dataframe(default_etfs[portfolio_type])

        # Create editable dataframe
        edited_df = st.data_editor(
            etf_data,
            column_config={
                'code': None,  # Hide the code column
                'name': st.column_config.TextColumn('ETF 이름', disabled=True),
                'current_price': st.column_config.NumberColumn('현재 가격', format='%d원'),
                'current_qty': st.column_config.NumberColumn('현재 수량', min_value=0),
                'current_value': None,
                'target_ratio': st.column_config.NumberColumn('목표 비율', disabled=True, format='%.2f%%'),
                'current_ratio': st.column_config.NumberColumn('현재 비율', disabled=True, format='%.2f%%'),
                'qty_to_trade': st.column_config.NumberColumn('추가 구매 수량', disabled=True, format='%d')
            },
            disabled=['name', 'current_value', 'target_ratio', 'current_ratio', 'qty_to_trade'],
            use_container_width=True
        )        
        
        if st.button(f'{portfolio_type} 리밸런싱 실행'):
            etf_list = edited_df.to_dict('records')
            # Recalculate rebalancing using the edited dataframe
            results, current_portfolio_value, update_portfolio_info = calculate_rebalancing(etf_list, total_deposit)
            
            # Save portfolio history
            portfolio_dashboard.save_portfolio_history(portfolio_type, current_portfolio_value + total_deposit)

            # Update portfolio info
            portfolio_info.update_portfolio_info(portfolio_type, update_portfolio_info)
            
            # Display results
            results_df = pd.DataFrame(results)

            # 컬럼명 변경
            results_df = results_df.rename(columns={
                'name': 'ETF 이름', 
                'current_ratio': '현재 비중', 
                'target_ratio': '목표 비중', 
                'qty_to_trade': '거래 수량'
            })
            
            st.subheader(f'{portfolio_type} 리밸런싱 결과')
            st.dataframe(
                results_df[['ETF 이름', '목표 비중', '현재 비중','거래 수량']].style.format({
                    '현재 비중': '{:.2%}',
                    '목표 비중': '{:.2%}',
                    '거래 수량': '{:,.0f}'
                }),
                use_container_width=True
            )
        # Portfolio history graph
            
        st.subheader(f'{portfolio_type} 누적 가치 히스토리')
        
        history_df = portfolio_dashboard.get_portfolio_history(portfolio_type)
        st.write(history_df)
        
        if not history_df.empty:
            history_df['date'] = pd.to_datetime(history_df['date'])
            fig = px.line(history_df, x='date', y='total_value',
                        title=f'{portfolio_type} 총 가치 추이',
                        labels={'total_value': '총 가치', 'date': '날짜'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("아직 포트폴리오 기록이 없습니다.")   # 각 탭에 대한 포트폴리오 대시보드 생성
    
    create_portfolio_tab(tab1, '개인연금')
    create_portfolio_tab(tab2, '퇴직연금')
    create_portfolio_tab(tab3, '코인')

if __name__ == "__main__":
    main()
