# file: app.py
from flask import Flask, request, jsonify, render_template

# Import các hàm chúng ta đã chuẩn bị
from utils import extract_tiki_ids_from_url
from tiki_crawler import scrape_tiki_reviews
from sentiment_analyzer import phan_tich_cam_xuc_dua_tren_sao

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
# === THÊM DÒNG NÀY ĐỂ HIỂN THỊ ĐÚNG TIẾNG VIỆT TRONG API ===
app.config['JSON_AS_ASCII'] = False
# Định nghĩa API endpoint /analyze, chỉ chấp nhận phương thức POST
@app.route('/')
def home():
    #Flask tự động tìm file index.html để chạy
    return render_template('index.html')
@app.route('/analyze', methods=['POST'])
def analyze_product():
    # 1. Nhận dữ liệu JSON từ request
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Vui lòng cung cấp 'url' trong body của request."}), 400
    
    url = data['url']

    # 2. "Dịch" URL thành các ID cần thiết
    product_id, spid = extract_tiki_ids_from_url(url)
    if not product_id:
        return jsonify({"error": "URL không hợp lệ hoặc không phải link sản phẩm Tiki."}), 400

    # 3. Gọi crawler để cào dữ liệu bình luận
    reviews = scrape_tiki_reviews(product_id, spid)
    if not reviews:
        return jsonify({"error": "Không thể cào được bình luận từ URL này."}), 500

    # 4. Phân tích cảm xúc và tính toán thống kê
    total_reviews = len(reviews)
    positive_count = 0
    neutral_count = 0
    negative_count = 0
    analyzed_reviews = []

    for review in reviews:
        sentiment = phan_tich_cam_xuc_dua_tren_sao(review['stars'])
        review['sentiment'] = sentiment # Thêm nhãn cảm xúc vào mỗi review
        analyzed_reviews.append(review)

        if sentiment == 'tích cực':
            positive_count += 1
        elif sentiment == 'trung tính':
            neutral_count += 1
        else:
            negative_count += 1

    # 5. Chuẩn bị kết quả cuối cùng để trả về
    result = {
        "status": "success",
        "stats": {
            "total_reviews": total_reviews,
            "positive": round((positive_count / total_reviews) * 100, 2) if total_reviews > 0 else 0,
            "neutral": round((neutral_count / total_reviews) * 100, 2) if total_reviews > 0 else 0,
            "negative": round((negative_count / total_reviews) * 100, 2) if total_reviews > 0 else 0,
        },
        "reviews": analyzed_reviews
    }

    # 6. Trả về kết quả dưới dạng JSON
    return jsonify(result)

# Chạy server khi file này được thực thi
if __name__ == '__main__':
    app.run(debug=True) # debug=True để server tự khởi động lại khi có thay đổi code```