import requests
import time
import math
from bs4 import BeautifulSoup

#-- HÀM LẤY THÔNG TIN SẢN PHẨM -- 
def _get_product_basic_info(product_url):
    """
    Hàm này truy cập trang HTML để lấy Tên và Ảnh đại diện sản phẩm.
    Sử dụng Meta Tags để đảm bảo độ ổn định cao nhất.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    }
    info = {"name": "Sản phẩm Tiki", "image_url": ""}
    
    try:
        response = requests.get(product_url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Lấy Tên sản phẩm từ thẻ meta og:title
            title_meta = soup.find('meta', property='og:title')
            if title_meta:
                info['name'] = title_meta.get('content', '').replace(' - Tiki', '')
            
            # 2. Lấy Ảnh sản phẩm từ thẻ meta og:image
            image_meta = soup.find('meta', property='og:image')
            if image_meta:
                info['image_url'] = image_meta.get('content', '')
            
            # Fallback: Nếu không thấy meta, tìm theo class 
            if not info['image_url']:
                # Tìm thẻ img có class bắt đầu bằng 'sc-' bên trong container ảnh
                img_tag = soup.find('img', attrs={'srcset': True}) 
                if img_tag:
                     # Lấy link đầu tiên trong srcset
                     info['image_url'] = img_tag.get('srcset').split(' ')[0]

    except Exception as e:
        print(f"Lỗi khi lấy thông tin sản phẩm (HTML): {e}")
    
    return info

# --- 2. HÀM TRINH SÁT API (QUAN TRỌNG ĐỂ LẤY ATTRIBUTE SUMMARY) ---
def _perform_reconnaissance_call(product_id, spid):
    """Gọi API 1 lần để lấy: Tổng quan sao, Attribute Summary."""
    base_url = "https://tiki.vn/api/v2/reviews"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'x-guest-token': '5lIwj7SGqix1tk6UJ2BMEr4gTXfzyevo',
    }
    # include 'stars' để lấy số lượng sao, 'attribute_vote_summary' để vẽ Radar
    params = {
        'limit': 1, 'page': 1, 'spid': spid, 'product_id': product_id,
        'include': 'comments,contribute_info,attribute_vote_summary,stars' 
    }
    response = requests.get(base_url, headers=headers, params=params)
    return response.json()

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
            if response.status_code != 200: break
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
def scrape_latest_reviews( product_url, product_id, spid):
    """
    Phân tích 1: Cào tối đa 300 bình luận mới nhất.
    """
    # 1. Lấy thông tin cơ bản (Tên, Ảnh) từ HTML
    product_info = _get_product_basic_info(product_url)
    print("Bắt đầu cào theo chiến lược MỚI NHẤT...")
 # 2. Lấy Attribute Summary từ API (Cần cho Radar Chart)
    attribute_summary = {}
    try:
        recon_data = _perform_reconnaissance_call(product_id, spid)
        attribute_summary = recon_data.get('attribute_vote_summary', {})
    except:
        pass

    # 3. Cào review
    reviews = _scrape_reviews_by_option(product_id, spid, 'id|desc', 300)
    
    # TRẢ VỀ ĐẦY ĐỦ 3 MÓN
    return {
        "product_info": product_info, 
        "reviews": reviews,
        "attribute_summary": attribute_summary
    }

def scrape_overview_reviews(product_url, product_id, spid, total_sample_size=400):
    """
    Phân tích 2: Dựa vào tỉ lệ số đánh giá các sao để lấy số lượng đánh giá tương ứng / 400 
    """
    print("Bắt đầu cào theo chiến lược TỔNG QUAN TỐI ƯU...")
    # 1. Lấy thông tin cơ bản (Tên, Ảnh) từ HTML
    product_info = _get_product_basic_info(product_url)
    
    try:
        # 1. Gọi API trinh sát: Lấy cả Stars count VÀ Attribute Summary cùng lúc
        # (Nhanh hơn là gọi 5 lần API để đếm trang)
        initial_data = _perform_reconnaissance_call(product_id, spid)
        attribute_summary = initial_data.get('attribute_vote_summary', {})
        
        # Lấy số lượng đánh giá từ key 'stars' (API Tiki đã đếm sẵn cho mình rồi!)
        rating_summary = initial_data.get('stars', {})
        rating_counts = {int(star): details['count'] for star, details in rating_summary.items()}
        
        print("Số lượng đánh giá từ API:", rating_counts)

        # 2. Tính tỷ lệ (Giữ nguyên logic của bạn)
        total_reviews_count = sum(rating_counts.values())
        if total_reviews_count == 0:
            return {"product_info": product_info, "reviews": [], "attribute_summary": attribute_summary}

        reviews_to_scrape = {}
        for star, count in rating_counts.items():
            proportion = count / total_reviews_count
            num_to_get = math.ceil(proportion * total_sample_size)
            reviews_to_scrape[star] = min(num_to_get, count)

        print("Kế hoạch cào:", reviews_to_scrape)

        # 3. Thực thi cào
        all_reviews = []
        for star in sorted(reviews_to_scrape.keys()):
            limit = reviews_to_scrape[star]
            if limit > 0:
                print(f"---> Cào {limit} review {star} sao...")
                reviews_for_star = _scrape_reviews_by_option(product_id, spid, f'stars|{star}', limit)
                all_reviews.extend(reviews_for_star)
        
        # TRẢ VỀ ĐẦY ĐỦ
        return {
            "product_info": product_info,
            "reviews": all_reviews,
            "attribute_summary": attribute_summary
        }

    except Exception as e:
        print(f"Lỗi tổng quan: {e}")
        # Fallback nếu lỗi thì chạy cào mới nhất
        return scrape_latest_reviews(product_url, product_id, spid)
    