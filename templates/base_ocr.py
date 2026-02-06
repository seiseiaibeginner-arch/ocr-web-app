"""通常OCRプロンプト定義"""

from ..utils.config import LANGUAGE_OPTIONS, OUTPUT_FORMAT_OPTIONS, DETAIL_OPTIONS


def build_ocr_prompt(language: str, output_format: str, detail: str) -> str:
    """
    通常OCR用のプロンプトを構築する
    
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
