import os
from flask import Flask, render_template, request
import whisper

app = Flask(__name__)

# アップロードされたファイルを一時保存する場所
UPLOAO_FOLDER = 'uploads'
os.makedirs(UPLOAO_FOLDER, exist_ok=True)

# Whisperモデルの読み込み
model = whisper.load_model("base")

# ⬇️【ここから追加 1】時間（秒）を「00:00:00」の表示にする処理 ---------------------
def format_timestamp(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
# ⬆️【ここまで追加 1】 ------------------------------------------------------------


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return "ファイルがありません", 400

    file = request.files['file']
    if file.filename == '':
        return "ファイルが選択せれていません", 400
    # ファイルを一時保存
    filepath = os.path.join(UPLOAO_FOLDER, file.filename)
    file.save(filepath)
            
    print(f"文字起こし開始: {file.filename}")
    # Whisperで解析
    result = model.transcribe(filepath)

    # 終わったら一時ファイルを削除
    if os.path.exists(filepath):
        os.remove(filepath)

    # ⬇️【ここから書き換え 2】時間と文字数を計算して組み立てる処理 ------------------
    formatted_segments = []

    for segment in result.get('segments', []):
        start_sec = segment['start']
        end_sec = segment['end']

        # しゃべっている時間（秒）を計算
        duration = round(end_sec - start_sec, 1)

        start_str = format_timestamp(start_sec)
        end_str = format_timestamp(end_sec)
        text = segment['text'].strip()
        char_count = len(text)

        # 「[00:00:00 -> 00:00:04]（4.0秒 / 22字）: テキスト...」の形式にする
        line = f"[{start_str} -> {end_str}] ({duration}秒 / {char_count}字) : {text}"
        formatted_segments.append(line)
    # ⬆️【ここまで書き換え 2】------------------------------------------------------

    # ★ 最後に結果を返す処理
    return render_template('index.html', result_text='\n'.join(formatted_segments))

if __name__ == '__main__':
    # サーバーの起動
    app.run(debug=True, port=5000)