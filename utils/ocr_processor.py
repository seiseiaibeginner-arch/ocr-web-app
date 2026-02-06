"""OCR処理モジュール - Google Gemini API連携"""

from google import genai
from PIL import Image
from typing import Tuple, Optional
from .config import GEMINI_MODEL, LANGUAGE_OPTIONS, OUTPUT_FORMAT_OPTIONS, DETAIL_OPTIONS


def build_prompt(language: str, output_format: str, detail: str) -> str:
    """
    OCR用のプロンプトを構築する
    
    Args:
        language: 言語設定キー
        output_format: 出力形式キー
        detail: 詳細度キー
    
    Returns:
        str: 構築されたプロンプト
    """
    lang_prefix = LANGUAGE_OPTIONS.get(language, "")
    format_type = OUTPUT_FORMAT_OPTIONS.get(output_format, "plain")
    detail_type = DETAIL_OPTIONS.get(detail, "exact")
    
    # ベースプロンプト
    base_prompt = "この画像内のすべての文字を正確に読み取ってください。"
    
    # 言語指定
    if lang_prefix:
        base_prompt = f"{lang_prefix}、{base_prompt}"
    
    # 出力形式指定
    if format_type == "markdown":
        base_prompt += "\n出力はマークダウン形式で整形してください。見出しやリスト、強調などを適切に使用してください。"
    elif format_type == "table":
        base_prompt += "\n表が含まれている場合は、マークダウンのテーブル形式で出力してください。"
    
    # 詳細度指定
    if detail_type == "summary":
        base_prompt += "\n読み取った内容の要約も最後に追加してください。"
    
    return base_prompt


def process_ocr(
    image: Image.Image,
    api_key: str,
    language: str = "自動検出",
    output_format: str = "プレーンテキスト",
    detail: str = "正確な転写"
) -> Tuple[bool, str]:
    """
    Gemini APIを使用してOCR処理を実行する
    
    Args:
        image: PIL Image オブジェクト
        api_key: Gemini API キー
        language: 言語設定
        output_format: 出力形式
        detail: 詳細度
    
    Returns:
        Tuple[bool, str]: (成功したかどうか, 結果テキストまたはエラーメッセージ)
    """
    if not api_key:
        return False, "APIキーが設定されていません。サイドバーでAPIキーを入力してください。"
    
    try:
        # Gemini クライアントを初期化
        client = genai.Client(api_key=api_key)
        
        # プロンプトを構築
        prompt = build_prompt(language, output_format, detail)
        
        # API呼び出し
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt, image]
        )
        
        # レスポンスからテキストを抽出
        if response and response.text:
            return True, response.text
        else:
            return False, "画像から文字を読み取れませんでした。画像の品質を確認してください。"
            
    except Exception as e:
        error_message = str(e)
        
        # エラーの種類に応じたメッセージ
        if "401" in error_message or "403" in error_message:
            return False, "APIキーが無効です。正しいAPIキーを入力してください。"
        elif "429" in error_message:
            return False, "APIのレート制限に達しました。しばらく時間をおいてから再実行してください。"
        elif "timeout" in error_message.lower():
            return False, "APIリクエストがタイムアウトしました。再度お試しください。"
        else:
            return False, f"OCR処理中にエラーが発生しました: {error_message}"


def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """
    APIキーの形式を簡易バリデーション
    
    Returns:
        Tuple[bool, str]: (有効かどうか, エラーメッセージ)
    """
    if not api_key:
        return False, "APIキーを入力してください"
    
    if len(api_key) < 10:
        return False, "APIキーが短すぎます"
    
    return True, ""
