import streamlit as st # フロントエンドを扱うstreamlitの機能をインポート
import requests # リクエストするための機能をインポート
from openai import OpenAI # openAIのchatGPTのAIを活用するための機能をインポート
from PIL import Image #画像を取り扱うためにインポート


# アクセスの為のキーをos.environ["OPENAI_API_KEY"]に代入し、設定

import os # OSが持つ環境変数OPENAI_API_KEYにAPIを入力するためにosにアクセスするためのライブラリをインポート
# ここにご自身のAPIキーを入力してください！
os.environ["OPENAI_API_KEY"]

# openAIの機能をclientに代入
client = OpenAI()

# ページ設定
st.set_page_config(page_title="ゆったりライド", page_icon=":train2:", layout="wide")

#駅名リストの作成
station_names = [] 


#ゆったりくんの画像
characterimg = Image.open('character.png')
answerimg = Image.open('answer.png')

#路線を取得
GetLinesUrl = "https://express.heartrails.com/api/json?method=getLines&area=%E9%96%A2%E6%9D%B1" # APIにリクエストするURLを作成　東京のcityコード
GetLinesResponse = requests.get(GetLinesUrl) # 作成したリクエスト用URLでアクセスして、responseに代入
lines_json = GetLinesResponse.json() # responseにjson形式の天気のデータが返ってくるので、response.json()をstations_jsonに代入
line_names = [] #リストの作成
for line in lines_json['response']['line']:
    line_names.append(line) #for文で全ての駅名をリストに格納

#駅名取得
def get_stations(lineSelection):
    url = "https://express.heartrails.com/api/json?method=getStations&line=" + lineSelection  # APIにリクエストするURLを作成　東京のcityコード
    response = requests.get(url) # 作成したリクエスト用URLでアクセスして、responseに代入
    stations_json = response.json() # responseにjson形式の天気のデータが返ってくるので、response.json()をstations_jsonに代入
    for station in stations_json['response']['station']:
        station_names.append(station['name']) #for文で全ての駅名をリストに格納
    return station_names

#ゆったタグ辞書
tag_type = {
    "ベビーカー":"ベビーカーがあります", 
    "朝":"朝の時間帯に移動します",
    "昼":"昼の時間帯に移動します",
    "夜":"夜の時間帯に移動します",
    "座りたい":"", 
    "人少なめ":"人が少ない時がいいです", 
    "ゆっくり乗換":"乗り換えに少し時間をかけたいです", 
    "エレベーター":"エレベーターが近いところで下車したいです", 
    "スーツケース":"スーツケースがあります", 
    "平日":"平日であることを想定してください", 
    "休日":"休日であることを想定してください"}


# chatGPTにリクエストするためのメソッドを設定。引数には出発駅と到着駅を記載
def run_gpt(from_station, content_kind_of_to_gpt, yutari_tagging):
    request_to_gpt = f"あなたは鉄道が大好きな社会人です。{from_station}から{destination_station}に通勤したいのですが、いつ電車に乗るとあまり混んでいないか教えて欲しいです。あと、何両目に乗るのが良いでしょうか？次の点も考慮して欲しいです。{yutari_tagging}ただし喋り方は小学生の男の子のようにして、150文字以内で答えてください。"

    # 決めた内容を元にclient.chat.completions.createでchatGPTにリクエスト。オプションとしてmodelにAIモデル、messagesに内容を指定
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": request_to_gpt },
        ],
    )

    # 返って来たレスポンスの内容はresonse.choices[0].message.content.strip()に格納されているので、これをoutput_contentに代入
    output_content = response.choices[0].message.content.strip()
    return output_content # 返って来たレスポンスの内容を返す

#ロゴの表示
img = Image.open('logo.png')
st.sidebar.image(img)


# 路線の選択
lineSelection = st.sidebar.selectbox(
    "路線名",
    options=line_names,
    index=line_names.index('JR京浜東北線') if 'JR京浜東北線' in line_names else 0
)
station_names = get_stations(lineSelection)

# タブの作成
tabs = st.tabs(["ていあん", "つかいかた"])

# 「ていあん」タブ

with tabs[0]:
    col1, col2, col3 = st.columns(3)


    # 出発地指定
    from_station = st.sidebar.selectbox("出発地",options=station_names)

    # 到着地指定
    destination_station = st.sidebar.selectbox("到着地",options=station_names)

    #ゆったりタグ設定
    yutari_tagging = st.sidebar.multiselect(
        "ゆったりタグ",
        options=list(tag_type.keys()),
        default=["ベビーカー", "朝"]
    )

    # 選択されたタグに対応する値を取得
    selected_tag_values = [tag_type[tag] for tag in yutari_tagging]

    if st.sidebar.button("ゆったり検索"):
        # 入力がすべて揃っている場合のみ処理を実行
        if from_station == destination_station:
            st.error("出発駅と到着駅が同じです。")
        elif from_station and destination_station:
            with st.spinner("ライドくん考え中..."):
                try:
                    output_content_text = run_gpt(from_station, destination_station, yutari_tagging)
                    st.success("ライドくんの答えがまとまりました！")
                    with col2:
                        st.image(characterimg)
                    st.image(answerimg)
                    st.write(output_content_text)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("乗車駅と降車駅を入力してください。")

# 「つかいかた」タブ
with tabs[1]:
    st.image(characterimg)
    st.title("ゆったりライドへようこそ！")
    st.write("混雑回避に特化した乗換案内アプリ、ベビーカーや大荷物でも安心して移動しましょう！")
    st.write("このアプリの使い方:")
    st.write("1. 路線名と出発地と到着地を選択してください。")
    st.write("2. タグをえらんでください。")
    st.write("3. 'ゆったり検索' ボタンをクリックして提案を確認します。")


