"""画像前処理モジュール"""

from PIL import Image
import io
from typing import Tuple, Optional
from .config import SUPPORTED_FORMATS, MAX_FILE_SIZE_BYTES


def validate_image(uploaded_file) -> Tuple[bool, str]:
    """
    アップロードされた画像のバリデーションを行う
    
    Returns:
        Tuple[bool, str]: (有効かどうか, エラーメッセージ)
    """
    if uploaded_file is None:
        return False, "ファイルが選択されていません"
    
    # ファイルサイズチェック
    file_size = uploaded_file.size
    if file_size > MAX_FILE_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        return False, f"ファイルサイズが上限を超えています（{size_mb:.1f}MB / 上限20MB）"
    
    # ファイル形式チェック
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension not in SUPPORTED_FORMATS:
        return False, f"非対応のファイル形式です。対応形式: {', '.join(SUPPORTED_FORMATS).upper()}"
    
    # 画像として読み込めるかチェック
    try:
        image = Image.open(uploaded_file)
        image.verify()
        uploaded_file.seek(0)  # ファイルポインタをリセット
        return True, ""
    except Exception as e:
        return False, f"画像ファイルを読み込めませんでした: {str(e)}"


def get_image_info(uploaded_file) -> dict:
    """
    画像のメタ情報を取得する
    
    Returns:
        dict: 画像情報（ファイル名、サイズ、形式、解像度）
    """
    try:
        image = Image.open(uploaded_file)
        info = {
            "filename": uploaded_file.name,
            "size_bytes": uploaded_file.size,
            "size_mb": round(uploaded_file.size / (1024 * 1024), 2),
            "format": image.format,
            "width": image.width,
            "height": image.height,
            "mode": image.mode
        }
        uploaded_file.seek(0)  # ファイルポインタをリセット
        return info
    except Exception:
        return {
            "filename": uploaded_file.name,
            "size_bytes": uploaded_file.size,
            "size_mb": round(uploaded_file.size / (1024 * 1024), 2),
            "format": "不明",
            "width": 0,
            "height": 0,
            "mode": "不明"
        }


def load_image(uploaded_file, max_dimension: int = 1920) -> Optional[Image.Image]:
    """
    アップロードされたファイルからPIL Imageを読み込む
    大きな画像は自動的にリサイズしてAPI負荷を軽減
    
    Args:
        uploaded_file: アップロードされたファイル
        max_dimension: 最大辺のピクセル数（デフォルト1920px）
    
    Returns:
        Optional[Image.Image]: 読み込んだ画像、失敗時はNone
    """
    try:
        image = Image.open(uploaded_file)
        
        # RGBに変換（透過PNGなどの対応）
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 大きな画像は縮小（API負荷軽減）
        width, height = image.size
        if width > max_dimension or height > max_dimension:
            # アスペクト比を維持してリサイズ
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    except Exception:
        return None
