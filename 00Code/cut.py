from PIL import Image
from pathlib import Path

def crop_image(input_path, output_path, crop_area):
    """
    裁切圖片並儲存結果。

    :param input_path: 原始圖片路徑
    :param output_path: 裁切後圖片的儲存路徑
    :param crop_area: 一個四元素的 tuple，格式為 (left, upper, right, lower)
    """
    try:
        output_path = Path(output_path)  # 確保是 Path 物件
        output_path.parent.mkdir(parents=True, exist_ok=True)  # 確保資料夾存在
        print(f"➡️ 輸出路徑：{output_path.resolve()}")
        
        # 開啟圖片
        with Image.open(input_path) as img:
            # 裁切圖片
            cropped_img = img.crop(crop_area)
            # 儲存裁切後的圖片
            cropped_img.save(output_path)
            print(f"✅ 圖片已裁切並儲存到 {output_path}")
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")


