# file: tiki_crawler.py
import requests
import time

def scrape_tiki_reviews(product_id, spid, page_limit=50):
    """
    Hàm này cào bình luận của một sản phẩm trên Tiki dựa vào ID.
    Nó trả về một list các dictionary chứa thông tin bình luận.
    """
    base_url = "https://tiki.vn/api/v2/reviews"
    all_reviews = []
    headers = {
        'User-Agent': 'Mozilla/5.0 ...', # Giữ lại header của bạn
        'x-guest-token': '...', # Giữ lại token của bạn
    }
    params = {
        'limit': 5,
        'page': 1,
        'spid': spid,
        'product_id': product_id,
        'seller_id': '1', # seller_id thường không quá quan trọng
    }

    print(f"Bắt đầu cào sản phẩm product_id={product_id}, spid={spid}")
    for page in range(1, page_limit + 1):
        params['page'] = page
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status() # Báo lỗi nếu request thất bại
            data = response.json()
            reviews_list = data.get('data', [])
            
            if not reviews_list:
                break
                
            for review in reviews_list:
                all_reviews.append({
                    'username': review.get('created_by', {}).get('name', 'N/A'),
                    'stars': review.get('rating'),
                    'comment': review.get('content', '').replace('\n', ' ')
                })
            time.sleep(0.5)
        except Exception as e:
            print(f"Lỗi khi cào trang {page}: {e}")
            break
            
    print(f"Cào xong, thu được {len(all_reviews)} bình luận.")
    return all_reviews