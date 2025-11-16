# file: download_model.py

from underthesea import sentiment

print("Bắt đầu quá trình tải mô hình phân tích cảm xúc của underthesea...")
print("Quá trình này chỉ cần chạy một lần duy nhất.")
print("Vui lòng đảm bảo bạn đang có kết nối Internet ổn định.")
print("Bạn sẽ thấy thanh tiến trình download xuất hiện bên dưới...")

try:
    # Chúng ta chỉ cần gọi hàm sentiment một lần với một câu bất kỳ
    # để kích hoạt quá trình tải về.
    sentiment("câu này chỉ dùng để kiểm tra và tải mô hình")
    
    print("\n-------------------------------------------------------------")
    print("THÀNH CÔNG! Mô hình đã được tải về và lưu vào cache.")
    print("Bây giờ bạn có thể chạy file 'sentiment_analyzer.py' bình thường.")
    print("-------------------------------------------------------------")

except Exception as e:
    print(f"\nĐÃ XẢY RA LỖI TRONG QUÁ TRÌNH TẢI: {e}")
    print("Vui lòng kiểm tra lại kết nối mạng, tường lửa và thử chạy lại script này.")