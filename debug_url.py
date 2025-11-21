# file này để chạy thử với các URL không có sid hoặc pid
import re
import requests

def extract_tiki_ids_from_url(url):
    try:
        print(f"--- Bắt đầu trích xuất ID từ: {url} ---")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        }
        
        print("Đang gửi request GET đến URL...")
        response = requests.get(url, headers=headers)
        
        # In ra status code để biết request có thành công không
        print(f"Request hoàn tất, Status Code: {response.status_code}")
        response.raise_for_status() # Nếu status code không phải 2xx sẽ báo lỗi
        
        html_content = response.text
        
        # In ra một vài trăm ký tự đầu 
        print("\n--- 500 ký tự đầu tiên của HTML ---")
        print(html_content[:500])
        print("---------------------------------\n")

        # Kiểm tra xem các chuỗi cần tìm có tồn tại không
        print(f"Kiểm tra sự tồn tại của '\"product_id\"': ", end="")
        if '"product_id"' in html_content:
            print("TÌM THẤY")
        else:
            print("KHÔNG TÌM THẤY!")

        product_id_match = re.search(r'"product_id":(\d+)', html_content)
        spid_match = re.search(r'"spid":(\d+)', html_content)
        
        if not product_id_match:
            print("!!! LỖI: Regex không tìm thấy product_id.")
            return None, None

        product_id = product_id_match.group(1)
        spid = spid_match.group(1) if spid_match else product_id
        
        print(f"--- Trích xuất thành công: product_id={product_id}, spid={spid} ---")
        return product_id, spid
        
    except requests.exceptions.HTTPError as http_err:
        print(f"!!! LỖI HTTP KHI TRUY CẬP URL: {http_err}")
        return None, None
    except Exception as e:
        print(f"!!! Lỗi không xác định: {e}")
        return None, None

# --- URL TEST THỬ  ---
test_url = "https://tiki.vn/tai-nghe-bluetooth-khong-day-cao-cap-hoco-eq1-pin-7h-am-thanh-song-dong-bass-chac-cam-ung-co-mic-den-led-sang-trong-hang-chinh-hang-p271995193.html"

print("\n=== BẮT ĐẦU KIỂM TRA ===")
pid, sid = extract_tiki_ids_from_url(test_url)

print("\n=== KẾT QUẢ CUỐI CÙNG ===")
print(f"Product ID: {pid}")
print(f"SPID: {sid}")