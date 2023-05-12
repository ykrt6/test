import streamlit as st
import cv2
import datetime
import time
from PIL import Image

import speech_recognition as sr

import dropbox

def linkDropbox() :
    dropbox_access_token="sl.BePulhajdb7X1pfNx2IL6-eNl7VDMTQeQUQNwX0l3c-XHefFFL5CAeAxDF0ZFOeG78jZ0AeRvruN_GPcxglBF8hyXLv_9SA6GZeGrlgTdoCX3g0t5X8rCMqvP6JvRkPWdV9bCG0"

    client = dropbox.Dropbox(dropbox_access_token, timeout=300)
    st.write("ドロップボックスアカウントがリンクされました")
    return client

def uploadDropbox(img, filename, client) :
    dropbox_path="/test/" + filename

    client.files_upload(img, dropbox_path)
    st.write(filename + "をアップロードしました")

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
    ret, img = cap.read()
    time.sleep(0.01)
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    image_loc.image(img)

    return img

def main() :
    # dropbox とリンク付け
    client = linkDropbox()

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
        img.save(".\\fig\\" + filename, "JPEG")
        with open(".\\fig\\" + filename, "rb") as f :
            image_bytes = f.read()  # バイナリ形式に変換
        uploadDropbox(image_bytes, filename, client)    # dropboxにアップロード

    # if st.checkbox("finish") :
        # break
    
    cap.release()
    cv2.destroyAllWindows()



if __name__ == "__main__" :
    main()
    
    # voice_text = record()

    # if voice_text == "あ" :
    #     capter()
    # else :
    #     st.warning(voice_text)
    