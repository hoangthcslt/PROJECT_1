# file: utils.py
import re
from urllib.parse import urlparse, parse_qs

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
        spid = query_params.get('spid', [product_id])[0] # Nếu không có spid, mặc định dùng product_id

        return product_id, spid
    except Exception as e:
        print(f"Lỗi khi trích xuất ID từ URL: {e}")
        return None, None