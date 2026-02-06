# 📝 画像 OCR 文字起こし Web アプリケーション

Streamlit + Google Gemini API (Gemini 2.0 Flash) を使用した OCR（光学文字認識）Webアプリケーション

## 🚀 機能

- **画像アップロード**: JPEG, PNG, GIF, BMP, WebP, TIFF対応（最大20MB）
- **複数ファイル対応**: 一度に複数の画像を処理可能
- **画像プレビュー**: アップロード画像のサムネイル表示
- **OCR処理**: Google Gemini 2.0 Flash のビジョン機能で文字認識
- **結果編集**: OCR結果をその場で編集可能
- **ダウンロード**: TXT / Markdown形式でダウンロード
- **クリップボードコピー**: ワンクリックでコピー

## 📋 必要要件

- Python 3.9以上
- Google Gemini API キー

## 🔧 セットアップ

### 1. 仮想環境の作成

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定（オプション）

`.env` ファイルを作成してAPIキーを設定できます：

```
GEMINI_API_KEY=your_api_key_here
```

## ▶️ 実行方法

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## 📖 使い方

1. サイドバーでGoogle Gemini APIキーを入力
2. OCRオプション（言語・出力形式・詳細度）を選択
3. 画像ファイルをアップロード
4. 「OCR実行」ボタンをクリック
5. 結果を確認・編集・ダウンロード

## 🔑 APIキーの取得

[Google AI Studio](https://aistudio.google.com/app/apikey) からAPIキーを取得してください。

## 📁 プロジェクト構成

```
ocr-app/
├── app.py                  # メインアプリケーション
├── requirements.txt        # 依存パッケージ
├── requirements.md         # 機能仕様書
├── .streamlit/
│   └── config.toml         # Streamlit設定
├── utils/
│   ├── __init__.py
│   ├── config.py           # 設定値管理
│   ├── image_handler.py    # 画像前処理
│   └── ocr_processor.py    # OCR処理
└── README.md
```

## ⚠️ 注意事項

- API利用には料金が発生する場合があります（無料枠あり）
- 手書き文字の精度は印刷文字より低くなる場合があります
- 大きな画像は処理に時間がかかる場合があります

## 📄 ライセンス

MIT License
