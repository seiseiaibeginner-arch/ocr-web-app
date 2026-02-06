"""vCard生成モジュール"""

from typing import Dict, List, Optional
import json
import csv
import io


def generate_vcard(data: Dict) -> str:
    """
    名刺データからvCard 3.0形式のテキストを生成する
    
    Args:
        data: 名刺データ辞書
    
    Returns:
        str: vCard形式のテキスト
    """
    lines = ["BEGIN:VCARD", "VERSION:3.0"]
    
    # 氏名
    name = data.get("name", "")
    if name:
        # 姓と名を分割（スペースで区切られている場合）
        name_parts = name.split()
        if len(name_parts) >= 2:
            lines.append(f"N:{name_parts[0]};{' '.join(name_parts[1:])};;;")
        else:
            lines.append(f"N:{name};;;;")
        lines.append(f"FN:{name}")
    
    # 会社名・部署
    company = data.get("company", "")
    department = data.get("department", "")
    if company or department:
        org_parts = [company, department] if department else [company]
        lines.append(f"ORG:{';'.join(org_parts)}")
    
    # 役職
    title = data.get("title", "")
    if title:
        lines.append(f"TITLE:{title}")
    
    # 電話番号（複数対応）
    phones = data.get("phone", [])
    if isinstance(phones, str):
        phones = [phones] if phones else []
    for phone in phones:
        if phone:
            lines.append(f"TEL;TYPE=WORK:{phone}")
    
    # 携帯電話
    mobile = data.get("mobile", "")
    if mobile:
        lines.append(f"TEL;TYPE=CELL:{mobile}")
    
    # FAX
    fax = data.get("fax", "")
    if fax:
        lines.append(f"TEL;TYPE=FAX:{fax}")
    
    # メール（複数対応）
    emails = data.get("email", [])
    if isinstance(emails, str):
        emails = [emails] if emails else []
    for email in emails:
        if email:
            lines.append(f"EMAIL:{email}")
    
    # Webサイト
    website = data.get("website", "")
    if website:
        lines.append(f"URL:{website}")
    
    # 住所
    address = data.get("address", "")
    if address:
        # 簡易的な住所フォーマット
        lines.append(f"ADR;TYPE=WORK:;;{address};;;;日本")
    
    lines.append("END:VCARD")
    
    return "\r\n".join(lines)


def generate_csv(data_list: List[Dict]) -> str:
    """
    名刺データリストからCSV形式のテキストを生成する
    
    Args:
        data_list: 名刺データのリスト
    
    Returns:
        str: CSV形式のテキスト
    """
    if not data_list:
        return ""
    
    # ヘッダー定義
    fieldnames = [
        "name", "name_kana", "company", "department", "title",
        "phone", "mobile", "fax", "email", "website", "address"
    ]
    
    # 日本語ヘッダー
    header_map = {
        "name": "氏名",
        "name_kana": "氏名（フリガナ）",
        "company": "会社名",
        "department": "部署",
        "title": "役職",
        "phone": "電話番号",
        "mobile": "携帯電話",
        "fax": "FAX",
        "email": "メール",
        "website": "Webサイト",
        "address": "住所"
    }
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # ヘッダー行
    writer.writerow([header_map.get(f, f) for f in fieldnames])
    
    # データ行
    for data in data_list:
        row = []
        for field in fieldnames:
            value = data.get(field, "")
            # リストの場合はカンマ区切りで結合
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value if v)
            row.append(value if value else "")
        writer.writerow(row)
    
    return output.getvalue()


def generate_json(data: Dict, indent: int = 2) -> str:
    """
    名刺データからJSON形式のテキストを生成する
    
    Args:
        data: 名刺データ辞書
        indent: インデント幅
    
    Returns:
        str: JSON形式のテキスト
    """
    return json.dumps(data, ensure_ascii=False, indent=indent)


def parse_business_card_response(response_text: str) -> Dict:
    """
    Gemini APIのレスポンスから名刺データを抽出する
    
    Args:
        response_text: APIレスポンステキスト
    
    Returns:
        Dict: 名刺データ辞書
    """
    # デフォルトの空データ
    default_data = {
        "name": None,
        "name_kana": None,
        "company": None,
        "department": None,
        "title": None,
        "phone": [],
        "mobile": None,
        "fax": None,
        "email": [],
        "website": None,
        "address": None
    }
    
    try:
        # JSONブロックを抽出
        text = response_text.strip()
        
        # マークダウンのコードブロックを除去
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()
        
        # JSONパース
        data = json.loads(text)
        
        # デフォルト値とマージ
        for key in default_data:
            if key not in data:
                data[key] = default_data[key]
        
        return data
    except json.JSONDecodeError:
        # JSONパースに失敗した場合はデフォルトを返す
        return default_data


def validate_business_card_data(data: Dict) -> bool:
    """
    名刺データが有効かどうかを検証する
    
    Returns:
        bool: 少なくとも1つのフィールドに値があればTrue
    """
    for key, value in data.items():
        if value:
            if isinstance(value, list) and len(value) > 0:
                return True
            elif isinstance(value, str) and value.strip():
                return True
    return False
