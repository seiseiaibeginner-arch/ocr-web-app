"""名刺テンプレート定義"""

# 名刺読み取り用プロンプト
BUSINESS_CARD_PROMPT = """
この名刺画像から以下の情報を読み取り、JSON形式で出力してください。
読み取れない項目はnullとしてください。
電話番号やメールアドレスが複数ある場合は配列で出力してください。

出力フォーマット（必ずこの形式のJSONのみを出力してください）:
{
    "name": "氏名",
    "name_kana": "氏名のフリガナ（あれば）",
    "company": "会社名",
    "department": "部署名",
    "title": "役職",
    "phone": ["電話番号1", "電話番号2"],
    "mobile": "携帯電話番号",
    "fax": "FAX番号",
    "email": ["メールアドレス1", "メールアドレス2"],
    "website": "WebサイトURL",
    "address": "住所（郵便番号含む）"
}
"""

# 抽出フィールドの定義
BUSINESS_CARD_FIELDS = {
    "name": {
        "label": "氏名",
        "type": "text",
        "required": True
    },
    "name_kana": {
        "label": "氏名（フリガナ）",
        "type": "text",
        "required": False
    },
    "company": {
        "label": "会社名",
        "type": "text",
        "required": False
    },
    "department": {
        "label": "部署",
        "type": "text",
        "required": False
    },
    "title": {
        "label": "役職",
        "type": "text",
        "required": False
    },
    "phone": {
        "label": "電話番号",
        "type": "list",
        "required": False
    },
    "mobile": {
        "label": "携帯電話",
        "type": "text",
        "required": False
    },
    "fax": {
        "label": "FAX",
        "type": "text",
        "required": False
    },
    "email": {
        "label": "メール",
        "type": "list",
        "required": False
    },
    "website": {
        "label": "Webサイト",
        "type": "text",
        "required": False
    },
    "address": {
        "label": "住所",
        "type": "textarea",
        "required": False
    }
}

# フィールドの表示順序
FIELD_ORDER = [
    "name", "name_kana", "company", "department", "title",
    "phone", "mobile", "fax", "email", "website", "address"
]
