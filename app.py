from flask import Flask, request, jsonify, render_template

# Import các hàm cần dùng
from utils import extract_tiki_ids_from_url, analyze_review_trends, calculate_radar_score
from tiki_crawler import scrape_latest_reviews, scrape_overview_reviews
from sentiment_analyzer import phan_tich_cam_xuc_dua_tren_sao

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# Định nghĩa API endpoint /analyze, phương thức POST
@app.route('/')
def home():
    #Flask sẽ tìm file index.html để thực hiện 
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_product():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Vui lòng cung cấp 'url'."}), 400
    
    url = data['url']
    # Nhận thông tin từ frontend, mặc định là 'latest'
    strategy = data.get('strategy', 'latest')

    product_id, spid = extract_tiki_ids_from_url(url)
    if not product_id:
        return jsonify({"error": "URL không hợp lệ hoặc không phải link sản phẩm Tiki."}), 400

    reviews = {}
    # Dựa vào strategy để gọi hàm crawler tương ứng
    if strategy == 'overview':
        reviews = scrape_overview_reviews(url,product_id, spid)
    else: 
        reviews = scrape_latest_reviews(product_id, spid)
    
    actual_reviews = reviews.get("reviews", [])
    if not actual_reviews:
        return jsonify({"error": "Không thể cào được bình luận từ URL này. Có thể sản phẩm không có bình luận nào."}), 400

    # Phần phân tích và tính toán các đánh giá
    total_reviews = len(actual_reviews)
    positive_count = 0
    neutral_count = 0
    negative_count = 0
    analyzed_reviews = []

    for review in actual_reviews:
        sentiment = phan_tich_cam_xuc_dua_tren_sao(review['stars'])
        review['sentiment'] = sentiment
        analyzed_reviews.append(review)

        if sentiment == 'tích cực':
            positive_count += 1
        elif sentiment == 'trung tính':
            neutral_count += 1
        else:
            negative_count += 1
    # HÀM PHÂN TÍCH XU HƯỚNG   
    trend_data = analyze_review_trends(actual_reviews)

    result = {
        "status": "success",
        "trend_data": trend_data,
        "stats": {
            "total_reviews": total_reviews,
            "positive": round((positive_count / total_reviews) * 100, 2) if total_reviews > 0 else 0,
            "neutral": round((neutral_count / total_reviews) * 100, 2) if total_reviews > 0 else 0,
            "negative": round((negative_count / total_reviews) * 100, 2) if total_reviews > 0 else 0,
        },
        "reviews": analyzed_reviews
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) # debug=True để server tự khởi động lại khi có thay đổi code```