# file: sentiment_analyzer.py

import pandas as pd
from underthesea import sentiment
import time

# --- Tên file dữ liệu đầu vào và đầu ra ---
# Hãy đảm bảo file này nằm cùng thư mục với script Python
input_filename = "tiki_reviews_274058672.csv" # << THAY TÊN FILE CỦA BẠN VÀO ĐÂY
output_filename = "tiki_reviews_analyzed.csv" # Tên file mới sẽ được tạo ra

# --- Xây dựng hàm phân tích cảm xúc ---
# Bọc logic vào một hàm giúp code sạch sẽ và dễ tái sử dụng
def phan_tich_cam_xuc(cau_binh_luan):
    # Xử lý trường hợp bình luận rỗng hoặc không phải là chuỗi
    if not isinstance(cau_binh_luan, str) or not cau_binh_luan.strip():
        return 'không xác định'
    
    # Dùng underthesea để phân loại
    return sentiment(cau_binh_luan)

# --- Bắt đầu xử lý file ---
try:
    # 1. Đọc file .csv bằng pandas
    print(f"Đang đọc file '{input_filename}'...")
    df = pd.read_csv(input_filename)
    print(f"Đọc thành công! Tìm thấy {len(df)} bình luận.")

    # 2. Áp dụng hàm phân tích cảm xúc vào cột 'comment'
    print("Bắt đầu phân tích cảm xúc (quá trình này có thể mất vài phút)...")
    start_time = time.time()
    
    # .apply() là một cách rất hiệu quả của pandas để áp dụng một hàm cho toàn bộ một cột
    # tqdm có thể giúp hiển thị thanh tiến trình nếu bạn có nhiều dữ liệu
    df['sentiment'] = df['comment'].apply(phan_tich_cam_xuc)
    
    end_time = time.time()
    print(f"Phân tích hoàn tất sau {end_time - start_time:.2f} giây.")

    # 3. Thống kê kết quả
    sentiment_counts = df['sentiment'].value_counts()
    print("\n--- Thống kê kết quả ---")
    print(sentiment_counts)
    print("-------------------------\n")

    # 4. Lưu DataFrame đã được cập nhật ra một file .csv mới
    print(f"Đang lưu kết quả vào file '{output_filename}'...")
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print("Lưu thành công!")
    print(f"\nMở file '{output_filename}' để xem kết quả với cột 'sentiment' mới.")

except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{input_filename}'. Hãy đảm bảo file này nằm cùng thư mục với script.")
except Exception as e:
    print(f"Đã xảy ra lỗi không mong muốn: {e}")