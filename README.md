# 🛍️ Insightify - E-commerce Analytics & Smart Comparison System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![Chart.js](https://img.shields.io/badge/Chart.js-4.0-orange)
![Status](https://img.shields.io/badge/Status-Completed-success)

> **Insightify** là một hệ thống phân tích và so sánh sản phẩm thương mại điện tử (End-to-End), giúp người dùng đưa ra quyết định mua sắm thông minh dựa trên dữ liệu thực tế thay vì cảm tính.

## 🌟 Tính Năng Nổi Bật (Key Features)

*   **📊 Phân tích Đánh giá Chuyên sâu:** Tự động thu thập hàng trăm đánh giá từ Tiki, phân loại cảm xúc (Tích cực/Tiêu cực) và thống kê tỷ lệ hài lòng.
*   **🔍 Reverse Engineering API:** Thay vì sử dụng các kỹ thuật HTML Parsing truyền thống (dễ lỗi), hệ thống khai thác các **Hidden API** của sàn TMĐT để lấy dữ liệu với tốc độ cao và độ chính xác tuyệt đối.
*   **⚔️ So sánh Đối đầu (Head-to-Head):** Chế độ so sánh trực quan giữa 2 sản phẩm trên các khía cạnh: Giá cả, Chất lượng, Mẫu mã, Dịch vụ.
*   **🕸️ Biểu đồ Mạng nhện (Radar Chart):** Trực quan hóa sức mạnh của sản phẩm trên 5 trục, giúp nhận diện điểm mạnh/yếu ngay lập tức.
*   **📈 Phân tích Xu hướng (Trend Analysis):** Theo dõi sự thay đổi chất lượng sản phẩm theo thời gian thực (Time-series) để phát hiện các lô hàng kém chất lượng.
*   **🤖 Trợ lý Gợi ý Cá nhân hóa:** Hệ thống sử dụng thuật toán **Weighted Scoring (Tính điểm trọng số)** để đưa ra lời khuyên mua hàng dựa trên ưu tiên riêng của người dùng (VD: Ưu tiên giá rẻ hay ưu tiên độ bền).
*   **🎨 Giao diện Modern UI:** Thiết kế hiện đại với Dark Mode/Light Mode, hiệu ứng Skeleton Loading mượt mà.

## 🛠️ Công Nghệ Sử Dụng (Tech Stack)

### Backend
*   **Ngôn ngữ:** Python
*   **Framework:** Flask (RESTful API Design)
*   **Data Processing:** Requests (Custom Headers/Cookies handling), Algorithm for Weighted Scoring.

### Frontend
*   **Core:** HTML5, CSS3 (CSS Variables for Dark Mode).
*   **Logic:** Vanilla JavaScript (ES6+, Async/Await).
*   **Visualization:** Chart.js (Doughnut, Radar, Line charts), WordCloud2.js.

## 🚀 Quá Trình Phát Triển (Development Journey)

Dự án được xây dựng và tối ưu hóa qua 6 giai đoạn (Sprints), thể hiện quá trình từ nghiên cứu đến hoàn thiện sản phẩm.

### Tuần 1: Nghiên cứu & Thiết kế Hệ thống
*   Nghiên cứu cấu trúc website TMĐT (Tiki).
*   Thiết kế kiến trúc hệ thống: Client-Server Model.
*   Thiết lập môi trường phát triển (Python venv, Git flow).

### Tuần 2: Xây dựng Core Crawler & Reverse Engineering
*   **Thử thách:** HTML của trang web thay đổi liên tục và render bằng JavaScript (Client-side rendering).
*   **Giải pháp:** Sử dụng DevTools để phân tích Network Traffic, tìm ra **Internal API** trả về JSON chứa dữ liệu review và thuộc tính sản phẩm.
*   **Kết quả:** Tăng tốc độ cào dữ liệu lên 500% so với Selenium/BeautifulSoup thuần túy.

### Tuần 3: Xử lý Dữ liệu & Logic Phân tích
*   Xây dựng thuật toán lấy mẫu phân tầng (Stratified Sampling) để đảm bảo dữ liệu đánh giá 1-5 sao được thu thập khách quan, không bị thiên lệch (Bias).
*   Xử lý dữ liệu thô từ API (Attribute Vote Summary) để trích xuất các từ khóa "Điểm cộng" và "Điểm trừ" chính xác do người dùng bình chọn.

### Tuần 4: Phát triển Backend API
*   Xây dựng các Endpoint: `/analyze` (phân tích đơn) và `/compare` (so sánh kép).
*   Tối ưu hóa cấu trúc JSON trả về để giảm tải cho Frontend.

### Tuần 5: Xây dựng Frontend & Trực quan hóa
*   Thiết kế giao diện Responsive.
*   Tích hợp Chart.js để vẽ biểu đồ tương tác.
*   Xử lý các trạng thái bất đồng bộ (Loading states, Error handling).

### Tuần 6: Nâng cao - Hệ thống Gợi ý Thông minh
*   Phát triển tính năng **So sánh nâng cao**: Biểu đồ Radar và Biểu đồ Xu hướng.
*   Cài đặt thuật toán gợi ý dựa trên input người dùng (User Preference-based Recommendation).

## ⚙️ Cài đặt và Chạy thử (Installation)

1.  **Clone repository:**
    ```bash
    git clone https://github.com/hoangthcslt/PROJECT_1.git
    cd insightify
    ```

2.  **Tạo môi trường ảo (Khuyến nghị):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Cài đặt thư viện:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Chạy ứng dụng:**
    ```bash
    python app.py
    ```
    Truy cập `http://127.0.0.1:5000` trên trình duyệt.

## 📸 Screenshots

| Trang chủ (Dark Mode) | Chế độ So sánh |
|:---:|:---:|
| ![Home](link_anh_home.png) | ![Compare](link_anh_compare.png) |

## 🔮 Hướng phát triển (Future Roadmap)
*   [ ] Mở rộng hỗ trợ cho Shopee và Lazada bằng Selenium/Puppeteer.
*   [ ] Tích hợp Deep Learning (PhoBERT) để phân tích cảm xúc sâu hơn cho các bình luận không có số sao.
*   [ ] Triển khai (Deploy) hệ thống lên Docker và Cloud (AWS/Render).

---
**Author:** [N.Đ.Hoàng]
