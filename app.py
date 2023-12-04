
import pandas as pd
import numpy as np
import streamlit as st

# --- 뉴스 기사 크롤링 ---------------------------------------------------------------

def naver_news_crawling(keyword,pages):
  try:
    chromeOptions_options = webdriver.ChromeOptions()	# 크롬 실행
    chromeOptions_options.add_argument("headless")	# 창을 띄우지 않고 실행

    # start수를 1, 11, 21, 31 ...만들어 주는 함수, 페이지 수를 의미
    count = pages 		# 올바른 range 동작을 위해 +1
    page = []			# 페이지 수

    for i in range(count):
        if i == 1:
            page.append(i)
        elif i > 1:
            page.append((i * 10) + 1)

    all_text=[]			# 기사 제목을 담을 리스트 생성
    for page_number in page:
        url = 'https://search.naver.com/search.naver?where=news&sm=tab_pge&query=' +\
              keyword + '&start='+str(page_number)

        response = requests.get(url)		# url 요청
        html_text = response.text		# html 형식으로 가져오기 위함
        soup = bs(html_text,'html.parser')	# BeautifulSoup 객체 생성

        titles = soup.select('a.news_tit')	# 가져오려는 태그를 찾아서 넣어준다.
        for title_sen in titles:
            title = title_sen.get_text()
            all_text.append(title)

    all_text = list(all_text)
    return all_text

  except Exception as e:
    st.write('오류ㅠㅠ : ' + e)
    errorPrint()

# --- chatGPT 세팅 ---------------------------------------------------------------

openai.api_key = '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'

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]

# --- 탭 출력 ---------------------------------------------------------------

def graphPrint(df, df_medium, df_change, df_all):
  with tab1:
    st.subheader(select_stock + '의 최근 주가')
    st.dataframe(df.tail())

    st.subheader(select_stock + '의 주가 변동')
    st.line_chart(df_medium, width=400, height=400)

    st.subheader(select_stock + '의 주가 변동 폭')
    st.area_chart(df_change)

    st.subheader(select_stock + '의 골든크로스 / 데드크로스')
    st.write('골든크로스 : 단기 이동 평균선이 장기 이동 평균선 위로 교차하는 차트 패턴. 단기적인 가격 움직임이 상승함에 따라 시장의 추세가 변하고 있으므로, 상승 추세 신호로 간주되어 좋은 매수 시점으로 예상됩니다.')
    st.write('데드크로스 : 단기 이동 평균선이 장기 이동 평균선 아래로 교차하는 차트 패턴. 하락 추세 신호로 간주되어 매도 시점으로 예상됩니다.')
    st.write('But, 모든 평균선은 강세 시장인지, 약세 시장인지에 따라 시사하는 바가 다르므로, 여러가지 지표들을 고려하여 신중하게 투자해야 합니다.')
    fig, ax = plt.subplots()
    cross_above = df_all[(df_all['MA20'] > df_all['MA50']) & (df_all['MA20'].shift(1) <= df_all['MA50'].shift(1))]
    cross_below = df_all[(df_all['MA20'] < df_all['MA50']) & (df_all['MA20'].shift(1) >= df_all['MA50'].shift(1))]
    ax.plot(df_all.index, df_all['Close'], label='Close Price', color='blue', linewidth=0.1)
    ax.plot(df_all.index, df_all['MA5'], label='5-Day MA', color='black', linewidth=0.3)
    ax.plot(df_all.index, df_all['MA20'], label='20-Day MA', color='green', linewidth=1)
    ax.plot(df_all.index, df_all['MA50'], label='50-Day MA', color='red', linewidth=1)
    ax.scatter(cross_above.index, cross_above['MA20'], marker='o', color='red', label='Golden-Cross Point', s=100, alpha=0.5)
    ax.scatter(cross_below.index, cross_below['MA20'], marker='o', color='blue', label='Dead-Cross Point', s=100, alpha=0.5)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    st.pyplot(fig)

  with tab2:
    dfList = df['Close'].tail(20).values.tolist()
    print(', '.join(map(str, dfList)))

    st.subheader(select_stock + '에 대해')
    prompt1 = select_stock + "는 어떤 기업이며 어떤 일을 보통 해?"
    response1 = get_completion(prompt1)
    st.write(response1)

    st.subheader(select_stock + ' 종목 분석')
    prompt2 = "주식 중 " + select_stock + "는 어떤 종목이야? 주로 어떤 성향의 투자자들이 관심을 갖는지, 단기 투자에 적절한지 장기 투자에 적절한지 정리해서 말해줘. 그리고 위의 내용을 바탕으로 " + select_stock + "에 투자할때의 팁을 말해줘. 경고 문구는 필요 없어."
    #response2 = get_completion(prompt2)
    #st.write(response2)

    keyword = select_stock
    pages = 10
    news_data = naver_news_crawling(keyword,pages)
    nouns_sen = []
    okt = Okt()
    for sen in news_data:
      nouns_sen.extend(okt.nouns(sen))
    count = Counter(nouns_sen).most_common(50)
    wc = WordCloud(font_path='/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
                  , background_color='white', max_font_size = 100, max_words = 55, relative_scaling=.5, width = 300, height = 300)
    cloud = wc.generate_from_frequencies(dict(count))	# 워드클라우드(단어빈도) 설정

    fig = plt.figure(figsize=(8, 8))  # 스트림릿에서 plot그리기
    plt.imshow(cloud, interpolation = 'bilinear')		# 이미지 설정
    plt.axis('off')			# x y 축 숫자 제거
    plt.show()
    st.pyplot(fig)

    st.subheader(select_stock + ' 주가 분석')
    prompt3 = select_stock + "의 최근 주가 변동은 20일 전부터 " + ', '.join(map(str, dfList)) + "와 같이 변화해왔어. 어떤 변동이 있었는지를 주가와 상승폭을 포함하여 설명하고, 앞으로의 전망은 어떨치 추측해줘."
    response3 = get_completion(prompt3)
    st.write(response3)

def errorPrint():
  with tab1:
    st.write(select_stock + '의 데이터가 없습니다!')

  with tab2:
    st.write(select_stock + '의 데이터가 없습니다!')

# --- 그래프 계산 ---------------------------------------------------------------

def calcurGraph():
  current_date = datetime.now().date()
  df = fdr.DataReader(stock_code, select_date, current_date)

  # 종가 제외하고 삭제. 5, 20, 50일 이동평균선 추가
  df_medium = df.drop(['Open', 'High', 'Low', 'Volume', 'Change'], axis=1)
  df_all = df_medium.copy()

  if st.sidebar.checkbox('5일 이동평균선'):
    df_medium['MA5'] = df_medium['Close'].rolling(window=5).mean()
  if st.sidebar.checkbox('20일 이동평균선'):
    df_medium['MA20'] = df_medium['Close'].rolling(window=20).mean()
  if st.sidebar.checkbox('50일 이동평균선'):
    df_medium['MA50'] = df_medium['Close'].rolling(window=50).mean()

  df_all['MA5'] = df_all['Close'].rolling(window=5).mean()
  df_all['MA20'] = df_all['Close'].rolling(window=20).mean()
  df_all['MA50'] = df_all['Close'].rolling(window=50).mean()

  # Change 빼고 삭제
  df_change = df.drop(['Open', 'High', 'Low', 'Volume', 'Close'], axis=1)

  graphPrint(df, df_medium, df_change, df_all)

# ---
# ---
# --- 기본 화면 출력 ---------------------------------------------------------------

st.set_page_config(layout="wide")

st.title('수익과 행복한 삶을 위한 주가 데이터 분석')

st.sidebar.title('옵션')
#select_stock = st.sidebar.selectbox(
#    '확인하고 싶은 종목을 선택하세요',
#    ['삼성전자','LG에너지솔루션','SK하이닉스']
#)
select_stock = st.sidebar.text_input('확인하고 싶은 종목 입력')
if not select_stock:
  select_stock = '삼성전자'
select_date = st.sidebar.selectbox(
    '확인하고 싶은 기간을 선택하세요',
    ['3년', '1년', '1달']
)

if select_date == '1달':
  select_date = '2023-11-01'
if select_date == '1년':
  select_date = '2023-01-01'
if select_date == '3년':
  select_date = '2021-01-01'

tab1, tab2= st.tabs(['현재 주가 정보' , '종목 설명'])

# --- 해당 옵션 계산 --------------------------------------------------------

stocks = fdr.StockListing('KOSPI')

try:
  stock_code = stocks[stocks['Name']==select_stock]['Code'].to_string(index=False).strip()
  calcurGraph()
except:
  errorPrint()
