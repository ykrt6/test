# streamlit系
import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av

# dropbox系
import dropbox
import io
import time
import datetime
import pandas as pd

# 画像処理系
import numpy as np
import cv2
from PIL import Image


## キャプチャーをするクラス
class VideoProcessor:

    def __init__(self) -> None:
        self.save_state = "保存しない"

    ## 画像アップロード
    def uploadDropbox(self, img, filename, client) :
        dropbox_path="/test/" + filename

        client.files_upload(img, dropbox_path, mode=dropbox.files.WriteMode('overwrite'))
        st.success(filename + "をアップロードしました")

    ## 保存
    def save(self, img) :
        now = datetime.datetime.now()
        now_second = now.second
        if now_second % 10 == 0 :
            filename = now.strftime('%Y%m%d_%H%M%S') + '.jpg'
            img_bytes = io.BytesIO()    # メモリ上でバイナリデータを扱う
            img.save(img_bytes, "JPEG")     # メモリ上に保存
            img_bytes = img_bytes.getvalue()  # バッファすべてを bytes として出力
            self.uploadDropbox(img_bytes, filename, client)    # dropboxにアップロード

    ## 画像処理
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        if self.save_state == "保存する" :
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            self.save(img)
            img = np.array(img)
            img = av.VideoFrame.from_ndarray(img, format="rgb24")
        else :
            img = av.VideoFrame.from_ndarray(img, format="bgr24")

        return img


## Dropbox アカウント情報入力
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


## Dropbox にリンク
def linkDropbox(app_key, app_secret, refresh_token) :
    rdbx = dropbox.Dropbox(oauth2_refresh_token=refresh_token, app_key=app_key, app_secret=app_secret)

    rdbx.refresh_access_token()

    dropbox_access_token= rdbx._oauth2_access_token

    client = dropbox.Dropbox(dropbox_access_token, timeout=300)
    st.success("ドロップボックスアカウントがリンクされました")
    return client


## メイン
def main(client) :
    # キャプチャーの準備
    # cap = cv2.VideoCapture(0)

    # while cap.isOpened :
    webrtc = webrtc_streamer(key="example", video_processor_factory=VideoProcessor, rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
    if webrtc.video_processor :
        webrtc.video_processor.save_state = st.radio(label='選択してください', options=('保存しない', '保存する'), index=0, horizontal=True)
    
    # cap.release()

if __name__ == "__main__" :
    # App key、App secret、更新用トークンを使ってアクセルトークンの自動更新
    app_key, app_secret, refresh_token = fileProcess()
   
    # dropbox とリンク付け
    client = linkDropbox(app_key, app_secret, refresh_token)

    # streamlit の仕様のため (気にしないで)
    main(client)
    