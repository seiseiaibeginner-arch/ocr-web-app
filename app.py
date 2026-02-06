"""
画像 OCR 文字起こし Web アプリケーション v1.1
Streamlit + Google Gemini API (Gemini 2.0 Flash)

新機能:
- カメラ撮影モード
- 名刺読み取りテンプレート
"""

import streamlit as st
from datetime import datetime
from PIL import Image
import json
from utils import (
    SUPPORTED_FORMATS,
    MAX_FILE_SIZE_MB,
    LANGUAGE_OPTIONS,
    OUTPUT_FORMAT_OPTIONS,
    DETAIL_OPTIONS,
    validate_image,
    get_image_info,
    load_image,
    process_ocr,
    validate_api_key,
    process_camera_image,
    get_camera_image_info,
    generate_vcard,
    generate_csv,
    generate_json,
    parse_business_card_response,
    validate_business_card_data
)
from templates import BUSINESS_CARD_PROMPT, BUSINESS_CARD_FIELDS, FIELD_ORDER

# ページ設定
st.set_page_config(
    page_title="画像 OCR 文字起こし",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    /* ベーススタイル */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .image-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .field-label {
        font-weight: bold;
        color: #333;
        margin-bottom: 0.25rem;
    }
    .null-field {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 0.25rem;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 0.5rem;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
    }
    
    /* モバイル対応（768px以下） */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
            text-align: center;
        }
        .sub-header {
            font-size: 0.95rem;
            text-align: center;
        }
        .image-info {
            padding: 0.75rem;
            font-size: 0.85rem;
        }
        .stButton > button {
            padding: 1rem 1.5rem;
            font-size: 1rem;
            min-height: 50px;
        }
        /* タブをタッチしやすく */
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1rem;
            font-size: 0.95rem;
        }
        /* 入力フィールドを大きく */
        .stTextInput input, .stTextArea textarea {
            font-size: 16px !important; /* iOS でズームを防ぐ */
        }
        /* カードのパディング調整 */
        .element-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }
    
    /* 小型スマホ対応（480px以下） */
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.5rem;
        }
        .sub-header {
            font-size: 0.85rem;
            margin-bottom: 1rem;
        }
        .stButton > button {
            padding: 0.875rem 1rem;
            font-size: 0.95rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.6rem 0.75rem;
            font-size: 0.85rem;
        }
    }
    
    /* タッチデバイス向け調整 */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button:hover {
            transform: none;
        }
        .stButton > button:active {
            transform: scale(0.98);
        }
        /* タップターゲットを大きく */
        .stSelectbox > div > div {
            min-height: 44px;
        }
        .stRadio > div > label {
            padding: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """セッション状態の初期化"""
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "ocr_results" not in st.session_state:
        st.session_state.ocr_results = {}
    if "business_card_data" not in st.session_state:
        st.session_state.business_card_data = {}


def render_sidebar():
    """サイドバーのレンダリング"""
    with st.sidebar:
        st.markdown("## ⚙️ 設定")
        
        # APIキー入力
        st.markdown("### 🔑 API キー")
        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            value=st.session_state.api_key,
            help="Google AI StudioからAPIキーを取得してください",
            placeholder="AIza..."
        )
        st.session_state.api_key = api_key
        
        if api_key:
            is_valid, msg = validate_api_key(api_key)
            if is_valid:
                st.success("✅ APIキー設定済み")
            else:
                st.warning(f"⚠️ {msg}")
        else:
            st.info("💡 APIキーを入力してOCRを開始")
        
        st.markdown("---")
        
        # テンプレート選択
        st.markdown("### 📋 テンプレート")
        template = st.selectbox(
            "処理モード",
            options=["通常OCR", "名刺読み取り"],
            index=0,
            help="名刺読み取りを選択すると、構造化された連絡先情報を抽出します"
        )
        
        # テンプレートの説明文を表示
        if template == "通常OCR":
            st.info("""
            📄 **通常OCRモード**
            
            画像内のすべての文字を読み取り、テキストとして出力します。
            
            • 書類、スクリーンショット、写真などに対応
            • 言語・出力形式・詳細度をカスタマイズ可能
            • TXT / Markdown 形式でダウンロード
            """)
        else:
            st.info("""
            📇 **名刺読み取りモード**
            
            名刺画像から連絡先情報を自動抽出し、構造化データとして出力します。
            
            • 氏名・会社名・役職・電話・メール等を自動認識
            • 抽出結果をフォームで編集可能
            • vCard / CSV / JSON 形式でエクスポート
            • 連絡先アプリに直接インポート可能
            """)
        
        st.markdown("---")
        
        # オプション設定（通常OCR時のみ表示）
        if template == "通常OCR":
            st.markdown("### 🎛️ OCR オプション")
            
            language = st.selectbox(
                "読み取り言語",
                options=list(LANGUAGE_OPTIONS.keys()),
                index=0,
                help="画像内の文字の言語を指定"
            )
            
            output_format = st.selectbox(
                "出力形式",
                options=list(OUTPUT_FORMAT_OPTIONS.keys()),
                index=0,
                help="OCR結果の出力形式を選択"
            )
            
            detail = st.selectbox(
                "詳細度",
                options=list(DETAIL_OPTIONS.keys()),
                index=0,
                help="転写の詳細度を選択"
            )
        else:
            language = "自動検出"
            output_format = "プレーンテキスト"
            detail = "正確な転写"
        
        st.markdown("---")
        
        # 対応形式情報
        st.markdown("### 📋 対応形式")
        st.caption(f"**形式**: {', '.join(f.upper() for f in SUPPORTED_FORMATS)}")
        st.caption(f"**最大サイズ**: {MAX_FILE_SIZE_MB}MB")
        
        return template, language, output_format, detail


def render_input_section():
    """入力セクションのレンダリング（タブ切り替え）"""
    tab1, tab2 = st.tabs(["📁 ファイルアップロード", "📷 カメラ撮影"])
    
    uploaded_files = []
    camera_image = None
    
    with tab1:
        st.markdown("### 📤 画像をアップロード")
        files = st.file_uploader(
            "ドラッグ＆ドロップまたはクリックしてファイルを選択",
            type=SUPPORTED_FORMATS,
            accept_multiple_files=True,
            help=f"対応形式: {', '.join(f.upper() for f in SUPPORTED_FORMATS)} | 最大サイズ: {MAX_FILE_SIZE_MB}MB"
        )
        if files:
            uploaded_files = files
    
    with tab2:
        st.markdown("### 📷 カメラで撮影")
        st.caption("💡 書類やホワイトボードをその場で撮影してOCR処理できます")
        
        camera_input = st.camera_input(
            "撮影してください",
            help="カメラのアクセスを許可してください"
        )
        
        if camera_input:
            camera_image = camera_input
            st.success("✅ 画像を撮影しました")
    
    return uploaded_files, camera_image


def render_preview_section(uploaded_files, camera_image):
    """プレビューセクションのレンダリング"""
    valid_files = []
    valid_camera = None
    
    # アップロードファイルのプレビュー
    if uploaded_files:
        st.markdown("### 🖼️ アップロード画像プレビュー")
        
        num_cols = min(len(uploaded_files), 4)
        cols = st.columns(num_cols)
        
        for idx, uploaded_file in enumerate(uploaded_files):
            col = cols[idx % num_cols]
            
            with col:
                is_valid, error_msg = validate_image(uploaded_file)
                
                if is_valid:
                    st.image(uploaded_file, use_container_width=True)
                    info = get_image_info(uploaded_file)
                    st.markdown(f"""
                    <div class="image-info">
                        <strong>{info['filename']}</strong><br>
                        📐 {info['width']} × {info['height']}px<br>
                        📦 {info['size_mb']} MB
                    </div>
                    """, unsafe_allow_html=True)
                    valid_files.append(uploaded_file)
                else:
                    st.error(f"❌ {uploaded_file.name}\n{error_msg}")
    
    # カメラ画像のプレビュー
    if camera_image:
        st.markdown("### 📷 撮影画像プレビュー")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(camera_image, use_container_width=True)
            info = get_camera_image_info(camera_image)
            st.markdown(f"""
            <div class="image-info">
                <strong>カメラ撮影</strong><br>
                📐 {info['width']} × {info['height']}px<br>
                📦 {info['size_mb']} MB
            </div>
            """, unsafe_allow_html=True)
        
        valid_camera = camera_image
    
    return valid_files, valid_camera


def render_business_card_form(data: dict, idx: int = 0):
    """名刺データ編集フォームのレンダリング"""
    edited_data = {}
    
    st.markdown("#### ✏️ 抽出結果を編集")
    
    for field_key in FIELD_ORDER:
        field_info = BUSINESS_CARD_FIELDS.get(field_key, {})
        label = field_info.get("label", field_key)
        field_type = field_info.get("type", "text")
        value = data.get(field_key)
        
        # 値の整形
        if value is None:
            display_value = ""
            is_null = True
        elif isinstance(value, list):
            display_value = ", ".join(str(v) for v in value if v)
            is_null = not display_value
        else:
            display_value = str(value)
            is_null = not display_value
        
        # フィールドタイプに応じた入力
        if field_type == "textarea":
            edited_value = st.text_area(
                f"{'⚠️ ' if is_null else ''}{label}",
                value=display_value,
                key=f"bc_{field_key}_{idx}",
                height=80
            )
        else:
            edited_value = st.text_input(
                f"{'⚠️ ' if is_null else ''}{label}",
                value=display_value,
                key=f"bc_{field_key}_{idx}"
            )
        
        # リスト形式のフィールドは配列に戻す
        if field_type == "list" and edited_value:
            edited_data[field_key] = [v.strip() for v in edited_value.split(",") if v.strip()]
        else:
            edited_data[field_key] = edited_value if edited_value else None
    
    return edited_data


def render_business_card_exports(data: dict, idx: int = 0):
    """名刺データエクスポートボタンのレンダリング"""
    st.markdown("#### 📥 ダウンロード")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # vCard
        vcard_text = generate_vcard(data)
        st.download_button(
            label="📇 vCard (.vcf)",
            data=vcard_text.encode("utf-8"),
            file_name=f"contact_{timestamp}.vcf",
            mime="text/vcard",
            key=f"dl_vcard_{idx}"
        )
    
    with col2:
        # JSON
        json_text = generate_json(data)
        st.download_button(
            label="📄 JSON",
            data=json_text.encode("utf-8"),
            file_name=f"contact_{timestamp}.json",
            mime="application/json",
            key=f"dl_json_{idx}"
        )
    
    with col3:
        # CSV
        csv_text = generate_csv([data])
        st.download_button(
            label="📊 CSV",
            data=csv_text.encode("utf-8-sig"),
            file_name=f"contact_{timestamp}.csv",
            mime="text/csv",
            key=f"dl_csv_{idx}"
        )
    
    # JSONプレビュー
    with st.expander("🔍 JSONプレビュー"):
        st.json(data)


def render_ocr_results(file_name: str, result_text: str, idx: int):
    """通常OCR結果セクションのレンダリング"""
    st.markdown(f"#### 📄 {file_name}")
    
    edited_text = st.text_area(
        "OCR結果（編集可能）",
        value=result_text,
        height=300,
        key=f"result_text_{idx}"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 TXTでダウンロード",
            data=edited_text.encode("utf-8"),
            file_name=f"ocr_result_{timestamp}.txt",
            mime="text/plain",
            key=f"download_txt_{idx}"
        )
    
    with col2:
        st.download_button(
            label="📥 Markdownでダウンロード",
            data=edited_text.encode("utf-8"),
            file_name=f"ocr_result_{timestamp}.md",
            mime="text/markdown",
            key=f"download_md_{idx}"
        )
    
    with st.expander("📋 コピー用テキスト"):
        st.code(edited_text, language=None)
    
    return edited_text


def process_business_card(image: Image.Image, api_key: str) -> tuple:
    """名刺画像を処理する"""
    from google import genai
    from utils.config import GEMINI_MODEL
    
    try:
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[BUSINESS_CARD_PROMPT, image]
        )
        
        if response and response.text:
            data = parse_business_card_response(response.text)
            if validate_business_card_data(data):
                return True, data
            else:
                return False, "名刺情報を抽出できませんでした。画像が名刺でない可能性があります。"
        else:
            return False, "APIからレスポンスを取得できませんでした。"
    
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "403" in error_msg:
            return False, "APIキーが無効です。"
        elif "429" in error_msg:
            return False, "APIのレート制限に達しました。"
        else:
            return False, f"エラー: {error_msg}"


def main():
    """メインアプリケーション"""
    init_session_state()
    
    # ヘッダー
    st.markdown('<p class="main-header">📝 画像 OCR 文字起こし</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Google Gemini 2.0 Flash を使用して画像内の文字を読み取ります</p>', unsafe_allow_html=True)
    
    # サイドバー
    template, language, output_format, detail = render_sidebar()
    
    # 入力セクション（タブ切り替え）
    uploaded_files, camera_image = render_input_section()
    
    # プレビュー
    valid_files, valid_camera = render_preview_section(uploaded_files, camera_image)
    
    # 処理対象があるか確認
    has_input = valid_files or valid_camera
    
    if has_input:
        st.markdown("---")
        
        # テンプレートに応じたボタンラベル
        button_label = "🚀 名刺読み取り実行" if template == "名刺読み取り" else "🚀 OCR実行"
        
        if st.button(button_label, use_container_width=True):
            if not st.session_state.api_key:
                st.error("⚠️ サイドバーでAPIキーを入力してください")
            else:
                st.markdown("### 📊 処理結果")
                
                # 処理対象リストを作成
                process_items = []
                
                for f in valid_files:
                    process_items.append(("file", f, f.name))
                
                if valid_camera:
                    process_items.append(("camera", valid_camera, "カメラ撮影"))
                
                # 各画像を処理
                for idx, (item_type, item, name) in enumerate(process_items):
                    with st.spinner(f"⏳ {name} を処理中..."):
                        # 画像読み込み
                        if item_type == "camera":
                            success, image, error = process_camera_image(item)
                            if not success:
                                st.error(f"❌ {name}: {error}")
                                continue
                        else:
                            image = load_image(item)
                            if image is None:
                                st.error(f"❌ {name}: 画像の読み込みに失敗しました")
                                continue
                        
                        # テンプレートに応じた処理
                        if template == "名刺読み取り":
                            success, result = process_business_card(
                                image, st.session_state.api_key
                            )
                            
                            if success:
                                st.success(f"✅ {name}: 名刺読み取り完了")
                                
                                col_img, col_form = st.columns([1, 2])
                                
                                with col_img:
                                    if item_type == "camera":
                                        st.image(item, use_container_width=True)
                                    else:
                                        st.image(item, use_container_width=True)
                                
                                with col_form:
                                    edited_data = render_business_card_form(result, idx)
                                    render_business_card_exports(edited_data, idx)
                            else:
                                st.error(f"❌ {name}: {result}")
                                st.info("💡 通常OCRモードで再試行することをお勧めします。")
                        else:
                            # 通常OCR処理
                            success, result = process_ocr(
                                image=image,
                                api_key=st.session_state.api_key,
                                language=language,
                                output_format=output_format,
                                detail=detail
                            )
                            
                            if success:
                                st.success(f"✅ {name}: OCR完了")
                                
                                col_img, col_text = st.columns([1, 2])
                                
                                with col_img:
                                    if item_type == "camera":
                                        st.image(item, use_container_width=True)
                                    else:
                                        st.image(item, use_container_width=True)
                                
                                with col_text:
                                    render_ocr_results(name, result, idx)
                            else:
                                st.error(f"❌ {name}: {result}")
                    
                    st.markdown("---")
    
    # フッター
    st.markdown("---")
    st.caption("💡 **Tip**: 高品質な画像を使用すると、より正確な結果が得られます。名刺は正面から撮影してください。")


if __name__ == "__main__":
    main()
