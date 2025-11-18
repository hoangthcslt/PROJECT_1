# file: download_CORRECT_model.py

from underthesea import sentiment

# Đây là tên của mô hình lớn, hiện đại hơn
# SA_GENERAL_V131 chính là cái chúng ta thấy trong thư mục lúc đầu
MODEL_NAME = "SA_GENERAL_V131" 

print(f"Bắt đầu quá trình tải ĐÚNG mô hình: '{MODEL_NAME}'...")
print("Quá trình này sẽ tải một file lớn (~420MB).")
print("Vui lòng đảm bảo bạn đang có kết nối Internet ổn định và kiên nhẫn chờ đợi.")
print("Bạn sẽ thấy thanh tiến trình download xuất hiện bên dưới...")

try:
    # Gọi hàm sentiment và chỉ định rõ model cần dùng
    sentiment("câu này chỉ dùng để tải mô hình lớn", model=MODEL_NAME)
    
    print("\n-------------------------------------------------------------")
    print(f"THÀNH CÔNG! Mô hình '{MODEL_NAME}' đã được tải về.")
    print("Bây giờ bạn có thể chạy file phân tích chính.")
    print("-------------------------------------------------------------")

except Exception as e:
    print(f"\nĐÃ XẢY RA LỖI TRONG QUÁ TRÌNH TẢI: {e}")
    print("Vui lòng kiểm tra lại kết nối mạng, tường lửa và thử chạy lại script này.")