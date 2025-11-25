import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from collections import defaultdict

def extract_tiki_ids_from_url(url):
    """
    Trích xuất product_id và spid từ một URL sản phẩm của Tiki.
    Trả về một tuple (product_id, spid) hoặc (None, None) nếu không tìm thấy.
    """
    try:
        # Sử dụng regex để tìm product_id (con số theo sau chữ '-p')
        match = re.search(r'-p(\d+)\.html', url)
        if not match:
            return None, None
        
        product_id = match.group(1)
        
        # Sử dụng thư viện urllib để phân tích các tham số query và tìm spid
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        spid = query_params.get('spid', [product_id])[0]

        return product_id, spid
    except Exception as e:
        print(f"Lỗi khi trích xuất ID từ URL: {e}")
        return None, None
def analyze_review_trends(reviews):
    """
    Hàm nhận vào danh sách review, nhóm theo tháng, 
    và tính số sao trung bình cho mỗi tháng.
    """
    if not reviews:
        return {"labels": [], "values": []}

    # Dictionary để lưu tổng số sao và số lượng review cho mỗi tháng
    # Ví dụ: '2023-10': {'total_stars': 15, 'count': 3}
    monthly_data = defaultdict(lambda: {'total_stars': 0, 'count': 0})

    for review in reviews:
        timestamp = review.get('created_at')
        stars = review.get('stars')
        
        if timestamp and stars:
            try:
                # Chuyển timestamp thành đối tượng datetime
                dt = datetime.fromtimestamp(timestamp)
                # Tạo key dạng "YYYY-MM" (ví dụ: "2023-10")
                month_key = dt.strftime('%Y-%m')
                
                monthly_data[month_key]['total_stars'] += stars
                monthly_data[month_key]['count'] += 1
            except Exception:
                continue

    # Sắp xếp dữ liệu theo thời gian (từ cũ đến mới)
    sorted_months = sorted(monthly_data.keys())

    labels = []
    values = []

    for month in sorted_months:
        data = monthly_data[month]
        average_star = round(data['total_stars'] / data['count'], 2)
        
        labels.append(month)
        values.append(average_star)

    return {
        "labels": labels, # Trục X: ["2023-01", "2023-02", ...]
        "values": values  # Trục Y: [4.5, 4.2, ...]
    }
# --- UPDATE 22/11 ----
def calculate_radar_score(stats, attribute_summary):
    """
    Hàm tính điểm (0-100) cho 5 trục của biểu đồ Radar.
    Dựa trên thống kê sao và các tag bình chọn của người dùng.
    """
    # 1. Trục HÀI LÒNG (Satisfaction): Lấy trực tiếp từ % tích cực
    score_satisfaction = stats.get('positive', 0)

    # Các trục còn lại mặc định là 50 (trung bình) nếu không có dữ liệu
    scores = {
        "Hài lòng": score_satisfaction,
        "Chất lượng": 50,
        "Giá cả": 50,
        "Mẫu mã": 50,
        "Giao hàng": 50
    }

    # Lấy danh sách bình chọn từ Tiki
    votes = attribute_summary.get('votes', [])
    if not votes:
        base_score = 70 if score_satisfaction > 80 else (40 if score_satisfaction < 40 else 50)
        return {k: (v if k == "Hài lòng" else base_score) for k, v in scores.items()} # Trả về mặc định nếu không có dữ liệu tag

    # Các từ khóa để gom nhóm (Keyword Mapping)
    keywords = {
        "Chất lượng": ["chất lượng", "bền", "tốt", "xịn", "chắc chắn", "ổn","tiết kiệm", "nhanh", "mạnh", "êm"],
        "Giá cả": ["giá", "rẻ", "đắt", "hợp lý", "tiền"],
        "Mẫu mã": ["đẹp", "mẫu", "thiết kế", "màu", "nhỏ gọn", "sang"],
        "Giao hàng": ["giao", "ship", "đóng gói", "vận chuyển", "hộp", "nhân viên", "cẩn thận"]
    }

    # Biến tạm để tính tổng điểm và số lượng tag cho mỗi nhóm
    temp_scores = {key: {"total_score": 0, "count": 0} for key in keywords}

    for vote in votes:
        attr_name = vote.get('attribute_name', '').lower()
        agree = vote.get('agree', 0)
        total = vote.get('total_vote', 0)
        
        if total == 0: continue

        # Tính điểm cho tag này: (Số người đồng ý / Tổng số người vote) * 100
        # Ví dụ: "Đẹp" có 80 đồng ý / 100 vote => 80 điểm
        tag_score = (agree / total) * 100

        # Kiểm tra xem tag này thuộc nhóm nào
        for category, keys in keywords.items():
            if any(k in attr_name for k in keys):
                temp_scores[category]["total_score"] += tag_score
                temp_scores[category]["count"] += 1
    
    # Tính điểm trung bình cho từng nhóm
    for category, data in temp_scores.items():
        if data["count"] > 0:
            scores[category] = round(data["total_score"] / data["count"], 2)
        else:
            # Nếu không có tag nào thuộc nhóm này, ta dùng một logic "suy diễn" nhẹ
            # Nếu Hài lòng cao (>80), các khía cạnh khác mặc định là 70 (khá tốt) thay vì 50
            if score_satisfaction > 80:
                scores[category] = 70
            elif score_satisfaction < 40:
                scores[category] = 40

    return scores