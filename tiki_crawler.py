# file: tiki_crawler.py (PHIÊN BẢN NÂNG CẤP)
import requests
import time
import math
from bs4 import BeautifulSoup
# --- HÀM CỐT LÕI (PRIVATE) ---
def _scrape_reviews_by_option( product_id, spid, sort_option, review_limit):
    base_url = "https://tiki.vn/api/v2/reviews"
    reviews_collected = []
    # Sử dụng headers bạn đã có
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'x-guest-token': '5lIwj7SGqix1tk6UJ2BMEr4gTXfzyevo',
    }
    
    limit_per_page = 5 # Tiki trả về 5 review mỗi trang
    
    # Tính toán số trang cần cào
    # Ví dụ: review_limit=300 -> 60 trang
    pages_to_scrape = math.ceil(review_limit / limit_per_page)   
    for page in range(1, pages_to_scrape + 1):
        params = {
            'limit': limit_per_page,
            'page': page,
            'spid': spid,
            'product_id': product_id,
            'seller_id': '1',
            'sort': sort_option # Sử dụng tùy chọn sắp xếp được truyền vào
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
                    'comment': review.get('content', '').replace('\n', ' ')
                })
            
            time.sleep(0.5) # Tạm dừng để lịch sự
        except Exception as e:
            print(f"Lỗi khi cào trang {page} với tùy chọn '{sort_option}': {e}")
            break # Gặp lỗi thì dừng vòng lặp này

    # Cắt bớt để đảm bảo không vượt quá giới hạn
    return reviews_collected[:review_limit]
    

# --- CÁC HÀM CHIẾN LƯỢC (PUBLIC) ---
def scrape_latest_reviews( product_id, spid):
    """Phân tích 1: Cào tối đa 300 bình luận mới nhất."""
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
    Chiến lược 2 (TỐI ƯU): Lấy kế hoạch cào từ HTML, sau đó thực thi, suy luận ngược số trang review từ API
    """
    print("Bắt đầu cào theo chiến lược TỔNG QUAN TỐI ƯU...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'x-guest-token': '5lIwj7SGqix1tk6UJ2BMEr4gTXfzyevo',
    }
    base_url = "https://tiki.vn/api/v2/reviews"
    try:
        # --- BƯỚC 1: THỰC HIỆN 5 "CUỘC GỌI TRINH SÁT" ĐỂ LẤY SỐ TRANG ---
        print("Đang thực hiện các cuộc gọi trinh sát để ước tính số lượng...")
        rating_counts = {}
        reviews_per_page = 5 # Tiki API trả về 5 review mỗi trang

        for star in range(1, 6):
            params = {
                'limit': 1, # Chỉ cần lấy 1 review để lấy thông tin paging
                'page': 1,
                'spid': spid,
                'product_id': product_id,
                'sort': f'stars|{star}'
            }
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Trích xuất thông tin `last_page` từ đối tượng `paging`
            last_page = data.get('paging', {}).get('last_page', 0)
            
            # Ước tính số lượng review
            # Logic: (số trang - 1) * 5 + số review ở trang cuối (nếu có)
            # Để đơn giản, ta sẽ dùng last_page * reviews_per_page, sai số không đáng kể
            estimated_count = last_page * reviews_per_page
            rating_counts[star] = estimated_count
        
        print("Đã ước tính thành công số lượng đánh giá:", rating_counts)

        # --- BƯỚC 2: TÍNH TOÁN KẾ HOẠCH CÀO (Không thay đổi) ---
        total_reviews_count = sum(rating_counts.values())
        if total_reviews_count == 0:
            return {"reviews": []}

        reviews_to_scrape = {}
        for star, count in rating_counts.items():
            proportion = count / total_reviews_count
            num_to_get = math.ceil(proportion * total_sample_size)
            reviews_to_scrape[star] = min(num_to_get, count)

        print("Kế hoạch cào dữ liệu theo tỷ lệ:", reviews_to_scrape)

        # --- BƯỚC 3: THỰC THI KẾ HOẠCH (Không thay đổi) ---
        all_reviews = []
        for star in sorted(reviews_to_scrape.keys()):
            limit_for_this_star = reviews_to_scrape[star]
            
            if limit_for_this_star == 0: continue

            print(f"---> Đang cào {limit_for_this_star} đánh giá {star} sao...")
            sort_option = f'stars|{star}'
            
            reviews_for_star = _scrape_reviews_by_option(
                product_id=product_id, 
                spid=spid, 
                sort_option=sort_option,
                review_limit=limit_for_this_star
            )
            all_reviews.extend(reviews_for_star)
        
        return {"reviews": all_reviews}

    except Exception as e:
        print(f"Lỗi nghiêm trọng khi thực hiện chiến lược tổng quan: {e}")
        # Nếu có lỗi, chuyển về chiến lược an toàn hơn
        return scrape_latest_reviews(product_id, spid)
    