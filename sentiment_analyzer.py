# file: sentiment_analyzer.py

def phan_tich_cam_xuc_dua_tren_sao(so_sao):
    """
    Hàm này nhận vào số sao đánh giá (một số) và trả về nhãn cảm xúc.
    Logic:
    - 4, 5 sao: tích cực
    - 3 sao: trung tính
    - 1, 2 sao: tiêu cực
    """
    try:
        # Chuyển đổi đầu vào thành số nguyên để so sánh
        rating = int(so_sao)
        
        if rating >= 4:
            return 'tích cực'
        elif rating == 3:
            return 'trung tính'
        else: # rating <= 2
            return 'tiêu cực'
            
    except (ValueError, TypeError):
        # Nếu đầu vào không phải là số (ví dụ: rỗng, chữ, None)
        # thì coi nó là trung tính
        return 'trung tính'

# --- Phần test để bạn kiểm tra nhanh ---
if __name__ == '__main__':
    print(f"5 sao -> Cảm xúc: {phan_tich_cam_xuc_dua_tren_sao(5)}")
    print(f"4 sao -> Cảm xúc: {phan_tich_cam_xuc_dua_tren_sao(4)}")
    print(f"3 sao -> Cảm xúc: {phan_tich_cam_xuc_dua_tren_sao('3')}") # Thử với chuỗi
    print(f"2 sao -> Cảm xúc: {phan_tich_cam_xuc_dua_tren_sao(2)}")
    print(f"1 sao -> Cảm xúc: {phan_tich_cam_xuc_dua_tren_sao(1)}")
    print(f"Không có sao -> Cảm xúc: {phan_tich_cam_xuc_dua_tren_sao(None)}")