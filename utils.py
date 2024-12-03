from datetime import datetime

def get_month_format():
  now = datetime.now()
    
  if now.day >= 25:
    # 25일 이후면 다음 달로 설정
    next_month = now.month + 1
    next_year = now.year
        
    # 12월을 넘어가는 경우 처리
    if next_month > 12:
      next_month = 1
      next_year += 1
        
    return f"{next_year}-{next_month:02d}"
  else:
    # 25일 전이면 현재 연-월 그대로 사용
    return now.strftime("%Y-%m")
