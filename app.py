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

#=== ROUTE CHO SO SÁNH ===
@app.route('/compare-page')
def compare_page():
    # Chạy file compare.html cho so sánh 
    return render_template('compare.html')

#=== API phân tích 1 sản phẩm ===
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
        reviews = scrape_latest_reviews(url, product_id, spid)
    
    actual_reviews = reviews.get("reviews", [])
    attribute_summary = reviews.get("attribute_summary", {})
    product_info = reviews.get("product_info")
    
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
    stats = {
        "total_reviews": total_reviews,
        "positive": round((positive_count / total_reviews) * 100, 2) if total_reviews > 0 else 0,
        "neutral": round((neutral_count / total_reviews) * 100, 2) if total_reviews > 0 else 0,
        "negative": round((negative_count / total_reviews) * 100, 2) if total_reviews > 0 else 0,
    }  
    trend_data = analyze_review_trends(actual_reviews)
    radar_data = calculate_radar_score(stats, attribute_summary)
    result = {
        "status": "success",
        "product_info": product_info,
        "attribute_summary" : attribute_summary,
        "trend_data": trend_data,
        "radar_data" : radar_data,
        "stats": stats,
        "reviews": analyzed_reviews
    }

    return jsonify(result)


# === API so sánh 2 sản phẩm ===
@app.route('/compare', methods=['POST'])
def compare_products():
    data = request.get_json()
    urls = data.get('urls') # Nhận vào một list các URL ['url1', 'url2']
    strategy = data.get('strategy', 'latest')

    if not urls or not isinstance(urls, list) or len(urls) < 2:
        return jsonify({"error": "Vui lòng cung cấp ít nhất 2 liên kết sản phẩm."}), 400

    comparison_results = []

    # Duyệt qua từng URL (tối đa 2 URL để demo cho nhanh)
    for url in urls[:2]:
        try:
            product_id, spid = extract_tiki_ids_from_url(url)
            if not product_id:
                comparison_results.append({"error": f"Link không hợp lệ: {url}"})
                continue

            # 1. Cào dữ liệu (Tái sử dụng logic)
            scraped_data = {}
            if strategy == 'overview':
                scraped_data = scrape_overview_reviews(url, product_id, spid)
            else:
                scraped_data = scrape_latest_reviews(url, product_id, spid)
            
            reviews = scraped_data.get("reviews", [])
            attribute_summary = scraped_data.get("attribute_summary", {})

            if not reviews:
                comparison_results.append({"error": f"Không cào được dữ liệu: {url}"})
                continue

            # 2. Tính toán thống kê (Stats)
            total = len(reviews)
            pos = sum(1 for r in reviews if phan_tich_cam_xuc_dua_tren_sao(r['stars']) == 'tích cực')
            neu = sum(1 for r in reviews if phan_tich_cam_xuc_dua_tren_sao(r['stars']) == 'trung tính')
            neg = sum(1 for r in reviews if phan_tich_cam_xuc_dua_tren_sao(r['stars']) == 'tiêu cực')
            
            stats = {
                "total_reviews": total,
                "positive": round((pos/total)*100, 2) if total else 0,
                "neutral": round((neu/total)*100, 2) if total else 0,
                "negative": round((neg/total)*100, 2) if total else 0
            }

            # 3. Tính toán dữ liệu nâng cao
            trend_data = analyze_review_trends(reviews)
            radar_data = calculate_radar_score(stats, attribute_summary) # <--- MỚI

            # 4. Đóng gói kết quả cho sản phẩm này
            # Lưu ý: Cần lấy tên sản phẩm để hiển thị. 
            # Ở bài trước ta đã bỏ product_info, nhưng ở chế độ so sánh, tên sản phẩm rất quan trọng.
            # Tạm thời ta sẽ dùng ID hoặc URL làm tên, hoặc bạn có thể bật lại phần lấy tên trong crawler.
            comparison_results.append({
                "url": url,
                "product_info": scraped_data.get("product_info"),
                "stats": stats,
                "attribute_summary": attribute_summary,
                "trend_data": trend_data,
                "radar_data": radar_data
            })

        except Exception as e:
            print(f"Lỗi xử lý {url}: {e}")
            comparison_results.append({"error": "Lỗi hệ thống"})

    return jsonify(comparison_results)
if __name__ == '__main__':
    app.run(debug=True) # debug=True để server tự khởi động lại khi có thay đổi code```