"""カメラ入力処理モジュール"""

from PIL import Image
from typing import Tuple, Optional
import io


def process_camera_image(camera_input) -> Tuple[bool, Optional[Image.Image], str]:
    """
    カメラ入力から画像を処理する
    
    Args:
        camera_input: st.camera_inputからの入力
    
    Returns:
        Tuple[bool, Optional[Image.Image], str]: (成功, 画像, エラーメッセージ)
    """
    if camera_input is None:
        return False, None, "画像が撮影されていません"
    
    try:
        # カメラ入力からPIL Imageを読み込み
        image = Image.open(camera_input)
        
        # RGBに変換（必要に応じて）
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[-1])
            else:
                background.paste(image)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        return True, image, ""
    except Exception as e:
        return False, None, f"カメラ画像の処理に失敗しました: {str(e)}"


def get_camera_image_info(camera_input) -> dict:
    """
    カメラ画像のメタ情報を取得する
    
    Returns:
        dict: 画像情報
    """
    try:
        image = Image.open(camera_input)
        camera_input.seek(0)
        
        # サイズを計算
        camera_input.seek(0, 2)  # ファイル末尾に移動
        size_bytes = camera_input.tell()
        camera_input.seek(0)  # 先頭に戻す
        
        return {
            "filename": "camera_capture.jpg",
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / (1024 * 1024), 2),
            "format": "JPEG",
            "width": image.width,
            "height": image.height,
            "mode": image.mode
        }
    except Exception:
        return {
            "filename": "camera_capture.jpg",
            "size_bytes": 0,
            "size_mb": 0,
            "format": "JPEG",
            "width": 0,
            "height": 0,
            "mode": "不明"
        }
