"""設定値管理モジュール"""

# 対応画像フォーマット
SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"]
SUPPORTED_MIME_TYPES = [
    "image/jpeg",
    "image/png", 
    "image/gif",
    "image/bmp",
    "image/webp",
    "image/tiff"
]

# ファイルサイズ上限（20MB）
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Gemini API設定
GEMINI_MODEL = "gemini-2.0-flash"
API_TIMEOUT = 60

# 言語オプション
LANGUAGE_OPTIONS = {
    "自動検出": "",
    "日本語": "日本語で",
    "英語": "英語で",
    "中国語": "中国語で",
    "韓国語": "韓国語で"
}

# 出力形式オプション
OUTPUT_FORMAT_OPTIONS = {
    "プレーンテキスト": "plain",
    "マークダウン": "markdown",
    "表形式（表が含まれる場合）": "table"
}

# 詳細度オプション
DETAIL_OPTIONS = {
    "正確な転写": "exact",
    "要約付き転写": "summary"
}
