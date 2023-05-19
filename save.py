import streamlit as st
import cv2
import datetime
import time
from PIL import Image
import io
import pandas as pd

# import speech_recognition as sr

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

def linkDropbox(app_key, app_secret, refresh_token) :
    rdbx = dropbox.Dropbox(oauth2_refresh_token=refresh_token, app_key=app_key, app_secret=app_secret)

    rdbx.refresh_access_token()

    dropbox_access_token= rdbx._oauth2_access_token

    client = dropbox.Dropbox(dropbox_access_token, timeout=300)
    st.success("ドロップボックスアカウントがリンクされました")
    return client

def uploadDropbox(img, filename, client) :
    dropbox_path="/test/" + filename

    client.files_upload(img, dropbox_path)
    st.success(filename + "をアップロードしました")

# def record() :
#     listener = sr.Recognizer()
#     try:
#         with sr.Microphone() as source:
#             st.write("Listening...")
#             voice = listener.listen(source)
#             voice_text = listener.recognize_google(voice, language="ja-JP")
#             st.write(voice_text)
#         return voice_text
#     except:
#         st.warning('sorry I could not listen')

def capter(cap, image_loc) -> Image :
    while(cap.isOpened()):
        ret, img = cap.read()
        if img is False:
            break
        time.sleep(0.01)
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        image_loc.image(img)

    return img

def fileProcess() -> str :
    uploaded_file = st.file_uploader("ファイルアップロード", type='csv')
    if uploaded_file is not None:
        # アップロードファイルをメインにデータ表示
        df = pd.read_csv(uploaded_file, encoding="shift-jis", header=None)
        if st.checkbox("データファイルの内容を表示") :    
            st.table(df)
    else :
        st.warning("データファイルをアップロードしてください")
        st.stop()
        
    app_key = df.loc[0,1]
    app_secret = df.loc[1,1]
    refresh_token = df.loc[2,1]

    return app_key, app_secret, refresh_token


def main(client) :
    # キャプチャーの準備
    cap = cv2.VideoCapture(0)
    image_loc = st.empty()

    # ラジオボタン
    option = st.selectbox("選択してください", ["none", "capter", "save"])
    st.write(option + "を選択中")
    
    if option == "capter" :
        while cap.isOpened :
            img = capter(cap, image_loc)    # キャプチャー
    elif option == "save" :
        filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.jpg'
        img = capter(cap, image_loc)
        img_bytes = io.BytesIO()    # メモリ上でバイナリデータを扱う
        img.save(img_bytes, "JPEG")     # メモリ上に保存
        img_bytes = img_bytes.getvalue()  # バッファすべてを bytes として出力
        uploadDropbox(img_bytes, filename, client)    # dropboxにアップロード
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__" :
    # update_access_token = False
    # client = ""

    # App key、App secret、更新用トークンを使ってアクセルトークンの自動更新
    app_key, app_secret, refresh_token = fileProcess()
   
    # dropbox とリンク付け
    client = linkDropbox(app_key, app_secret, refresh_token)

    # streamlit の仕様のため
    main(client)
        

    
    # voice_text = record()

    # if voice_text == "あ" :
    #     capter()
    # else :
    #     st.warning(voice_text)
    