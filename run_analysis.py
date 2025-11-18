# file: run_analysis.py

import csv
# Thay đổi import: gọi hàm mới từ sentiment_analyzer
from sentiment_analyzer import phan_tich_cam_xuc_dua_tren_sao 

# --- Cấu hình file (giữ nguyên) ---
INPUT_CSV_FILE = 'tiki_reviews_274058672.csv' 
OUTPUT_CSV_FILE = 'tiki_reviews_analyzed_simple.csv' # Đổi tên file output cho rõ

def analyze_csv_data(input_file, output_file):
    print(f"Bắt đầu quá trình phân tích file '{input_file}' bằng logic số sao...")
    
    processed_data = []
    
    try:
        with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            original_fieldnames = reader.fieldnames
            
            for row in reader:
                # Lấy số sao từ cột 'stars'
                star_rating = row.get('stars')
                
                # Gọi hàm phân tích mới, truyền vào số sao thay vì bình luận
                sentiment_label = phan_tich_cam_xuc_dua_tren_sao(star_rating)
                
                row['sentiment'] = sentiment_label
                processed_data.append(row)
        
        print(f"Đã phân tích xong {len(processed_data)} bình luận.")
        
        if processed_data:
            new_fieldnames = original_fieldnames + ['sentiment']
            
            # Sử dụng utf-8-sig để Excel đọc tiếng Việt tốt
            with open(output_file, mode='w', newline='', encoding='utf-8-sig') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
                writer.writeheader()
                writer.writerows(processed_data)
            
            print(f"Đã lưu kết quả thành công vào file '{output_file}'")
            
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{input_file}'.")
    except Exception as e:
        print(f"Đã có lỗi xảy ra: {e}")

# --- Chạy hàm chính ---
if __name__ == '__main__':
    analyze_csv_data(INPUT_CSV_FILE, OUTPUT_CSV_FILE)