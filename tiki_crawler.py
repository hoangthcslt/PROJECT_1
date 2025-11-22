import requests
import time
import math
from bs4 import BeautifulSoup
# --- HÀM CỐT LÕI ---
def _scrape_reviews_by_option( product_id, spid, sort_option, review_limit):
    base_url = "https://tiki.vn/api/v2/reviews"
    reviews_collected = []
    # Sử dụng headers đã phân tích được
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'x-guest-token': '5lIwj7SGqix1tk6UJ2BMEr4gTXfzyevo',
    }
    
    limit_per_page = 5 # Tiki trả về 5 review mỗi trang
    
    # Tính toán số trang cần cào
    pages_to_scrape = math.ceil(review_limit / limit_per_page)   
    for page in range(1, pages_to_scrape + 1):
        params = {
            'limit': limit_per_page,
            'page': page,
            'spid': spid,
            'product_id': product_id,
             #'seller_id': '1',
            'sort': sort_option # Sử dụng tùy chọn sắp xếp được chọn
        }
        
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            reviews_list = data.get('data', [])

            if not reviews_list:
                # Nếu hết bình luận trước khi đạt giới hạn, dừng lại
                break 
            
            for review in reviews_list:
                reviews_collected.append({
                    'username': review.get('created_by', {}).get('name', 'N/A'),
                    'stars': review.get('rating'),
                    'comment': review.get('content', '').replace('\n', ' '),
                    'created_at': review.get('created_at'),
                    'id': review.get('id')
                })
            
            time.sleep(0.5) # Tạm dừng 0.5s để tránh bị chặn api
        except Exception as e:
            print(f"Lỗi khi cào trang {page} với tùy chọn '{sort_option}': {e}")
            break # Gặp lỗi thì dừng

    # Đảm bảo không vượt quá giới hạn đánh giá tối đa cần lấy
    return reviews_collected[:review_limit]
    

# --- CÁC HÀM LỰA CHỌN HƯỚNG PHÂN TÍCH ---
def scrape_latest_reviews( product_id, spid):
    """
    Phân tích 1: Cào tối đa 300 bình luận mới nhất.
    """
    print("Bắt đầu cào theo chiến lược MỚI NHẤT...")
    reviews = _scrape_reviews_by_option(
        product_id=product_id, 
        spid=spid, 
        sort_option='id|desc',  # Sắp xếp theo ID giảm dần = mới nhất
        review_limit=300
    )
    return {"reviews": reviews}

def scrape_overview_reviews(product_url, product_id, spid, total_sample_size=400):
    """
    Phân tích 2: Dựa vào tỉ lệ số đánh giá các sao để lấy số lượng đánh giá tương ứng / 400 
    """
    print("Bắt đầu cào theo chiến lược TỔNG QUAN TỐI ƯU...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'x-guest-token': '5lIwj7SGqix1tk6UJ2BMEr4gTXfzyevo',
    }
    base_url = "https://tiki.vn/api/v2/reviews"
    try:
        # --- 1. THỰC HIỆN 5 LẦN GỌI API ĐỂ LẤY SỐ TRANG CỦA TỪNG LOẠI SAO ---
        print("Đang thực hiện các cuộc gọi API để ước tính số lượng...")
        rating_counts = {}
        reviews_per_page = 5 # Tiki API hiển thị 5 review/ page

        for star in range(1, 6):
            params = {
                'limit': 1, # Chỉ cần 1 review để lấy thông tin paging
                'page': 1,
                'spid': spid,
                'product_id': product_id,
                'sort': f'stars|{star}'
            }
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Trích xuất thông tin `last_page` từ `paging`
            last_page = data.get('paging', {}).get('last_page', 0)
            
            # Ước tính số lượng review
            # Logic: ta sẽ dùng last_page * reviews_per_page, sai số không đáng kể
            estimated_count = last_page * reviews_per_page
            rating_counts[star] = estimated_count
        
        print("Đã ước tính thành công số lượng đánh giá:", rating_counts)

        # --- 2: TÍNH TỈ LỆ CÁC ĐÁNH GIÁ ĐỂ CÀO ---
        total_reviews_count = sum(rating_counts.values()) #TỔNG SỐ ĐÁNH GIÁ CỦA SP
        if total_reviews_count == 0:
            return {"reviews": []}

        reviews_to_scrape = {}
        for star, count in rating_counts.items():
            proportion = count / total_reviews_count # TỈ LỆ ĐÁNH GIÁ TỪNG SAO / TỔNG SỐ ĐÁNH GIÁ
            num_to_get = math.ceil(proportion * total_sample_size) # LẤY TỈ LỆ ĐÓ NHÂN VỚI 400(total_sample_size) ĐỂ RA SỐ ĐÁNH GIÁ LẤY TỐI ĐA CỦA SAO ĐÓ
            reviews_to_scrape[star] = min(num_to_get, count) # VỚI TRƯỜNG HỢP total_reviews_count < 400 THÌ SẼ LẤY HẾT SỐ ĐÁNH GIÁ

        print("Cào dữ liệu theo tỷ lệ:", reviews_to_scrape)

        # --- 3: THỰC THI KẾ HOẠCH (Không thay đổi) ---
        all_reviews = []
        for star in sorted(reviews_to_scrape.keys()): # SORT MẢNG reviews_to_scrape ĐỂ ƯU TIÊN CÀO TỪ 1 SAO ĐẾN 5 SAO
            limit_for_this_star = reviews_to_scrape[star]
            
            if limit_for_this_star == 0: continue # NẾU SỐ SAO ĐÓ KO CÓ ĐÁNH GIÁ NÀO THÌ SANG SAO KHÁC

            print(f"---> Đang cào {limit_for_this_star} đánh giá {star} sao...")
            sort_option = f'stars|{star}'
            
            reviews_for_star = _scrape_reviews_by_option( # GỌI HÀM CHÍNH 
                product_id=product_id, 
                spid=spid, 
                sort_option=sort_option,
                review_limit=limit_for_this_star
            )
            all_reviews.extend(reviews_for_star)
        
        return {"reviews": all_reviews}

    except Exception as e:
        print(f"Lỗi khi thực hiện chiến phân tích tổng quan: {e}")
        # Nếu có lỗi, chuyển về phân tích mới nhất
        return scrape_latest_reviews(product_id, spid)
    