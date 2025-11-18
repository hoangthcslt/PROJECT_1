// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    // === Lấy các element từ HTML ===
    const urlInput = document.getElementById('product-url');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultSection = document.getElementById('result-section');
    const skeletonLoader = document.getElementById('skeleton-loader');
    const errorMessage = document.getElementById('error-message');
    const resultContent = document.getElementById('result-content');
    const statsSummary = document.getElementById('stats-summary');
    const reviewsList = document.getElementById('reviews-list');
    const chartCanvas = document.getElementById('sentiment-chart');
    const wordCloudContainer = document.getElementById('wordcloud-container');
    const darkModeToggle = document.getElementById('dark-mode-toggle');

    let sentimentChart = null; // Biến để lưu trữ đối tượng biểu đồ

    // === Hàm tiện ích ===
    const showElement = (el) => el.classList.remove('hidden');
    const hideElement = (el) => el.classList.add('hidden');
    const addClass = (el, className) => el.classList.add(className);
    const removeClass = (el, className) => el.classList.remove(className);

    // === Logic cho Dark Mode ===
    const enableDarkMode = () => {
        document.body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
    };
    const disableDarkMode = () => {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('theme', 'light');
    };

    darkModeToggle.addEventListener('click', () => {
        if (document.body.classList.contains('dark-mode')) {
            disableDarkMode();
        } else {
            enableDarkMode();
        }
    });

    // Kiểm tra theme đã lưu khi tải trang
    if (localStorage.getItem('theme') === 'dark') {
        enableDarkMode();
    }
    
    // === Logic xử lý chính ===
    analyzeBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if (!url) {
            alert('Vui lòng nhập URL sản phẩm!');
            return;
        }

        // 1. Chuẩn bị giao diện
        showElement(resultSection);
        showElement(skeletonLoader);
        hideElement(errorMessage);
        hideElement(resultContent);
        removeClass(resultContent, 'fade-in');
        analyzeBtn.disabled = true;

        try {
            // 2. Gửi yêu cầu đến API
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url }),
            });
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Có lỗi xảy ra, vui lòng thử lại.');
            }
            
            // 3. Hiển thị kết quả
            setTimeout(() => { // Thêm độ trễ nhỏ để người dùng thấy hiệu ứng
                hideElement(skeletonLoader);
                displayResults(result);
                showElement(resultContent);
                addClass(resultContent, 'fade-in');
            }, 500);

        } catch (error) {
            hideElement(skeletonLoader);
            showElement(errorMessage);
            errorMessage.textContent = error.message;
        } finally {
            analyzeBtn.disabled = false;
        }
    });

    // === Các hàm hiển thị ===
    function displayResults(data) {
        // Stats
        statsSummary.innerHTML = `
            <p><strong>Tổng số đánh giá:</strong> ${data.stats.total_reviews}</p>
            <p><i class="ph ph-smiley" style="color:var(--green-color)"></i><strong>Hài lòng:</strong> ${data.stats.positive}%</p>
            <p><i class="ph ph-smiley-meh" style="color:var(--yellow-color)"></i><strong>Bình thường:</strong> ${data.stats.neutral}%</p>
            <p><i class="ph ph-smiley-sad" style="color:var(--red-color)"></i><strong>Không hài lòng:</strong> ${data.stats.negative}%</p>
        `;
        // Chart
        drawChart(data.stats);
        // Reviews
        displayReviews(data.reviews);
        // Word Cloud
        drawWordCloud(data.reviews);
    }

    function displayReviews(reviews) {
        reviewsList.innerHTML = '';
        if (reviews && reviews.length > 0) {
            reviews.forEach(review => {
                let sentimentClass = '';
                if (review.sentiment === 'tích cực') sentimentClass = 'sentiment-positive';
                else if (review.sentiment === 'trung tính') sentimentClass = 'sentiment-neutral';
                else sentimentClass = 'sentiment-negative';

                const reviewElement = document.createElement('div');
                reviewElement.className = 'review';
                reviewElement.innerHTML = `
                    <div class="review-header">
                        <span class="review-author">${review.username}</span>
                        <span class="review-sentiment ${sentimentClass}">${review.sentiment}</span>
                    </div>
                    <p>${review.comment || 'Không có bình luận'}</p>
                `;
                reviewsList.appendChild(reviewElement);
            });
        } else {
            reviewsList.innerHTML = '<p>Không có bình luận nào để hiển thị.</p>';
        }
    }

    function drawChart(stats) {
        if (sentimentChart) sentimentChart.destroy();
        sentimentChart = new Chart(chartCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Hài lòng', 'Bình thường', 'Không hài lòng'],
                datasets: [{
                    data: [stats.positive, stats.neutral, stats.negative],
                    backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: { legend: { display: false } }
            }
        });
    }

// Thay thế hàm này trong file static/js/script.js

function drawWordCloud(reviews) {
    // === BƯỚC KIỂM TRA AN TOÀN ===
    if (typeof WordCloud !== 'function') {
        console.error("Thư viện WordCloud2.js chưa được tải thành công.");
        wordCloudContainer.innerHTML = '<p style="text-align:center; color: var(--red-color);">Không thể tải thư viện Word Cloud.</p>';
        return; // Dừng hàm lại
    }
    // =============================

    const stopWords = ['và', 'là', 'của', 'có', 'mình', 'sản', 'phẩm', 'này', 'rất', 'cũng', 'nhưng', 'được', 'cho', 'không', 'đã', 'thì', 'quá', 'với', 'hàng', 'giao', 'shop'];
    const text = reviews.map(r => r.comment || '').join(' ').toLowerCase();
    const words = text.split(/\s+/).filter(word => word.length > 2 && !stopWords.includes(word));
    
    const wordFrequencies = words.reduce((map, word) => {
        map[word] = (map[word] || 0) + 1;
        return map;
    }, {});

    const list = Object.entries(wordFrequencies).sort((a, b) => b[1] - a[1]).slice(0, 50);

    if (list.length > 5) { // Cần ít nhất vài từ để vẽ
        WordCloud(wordCloudContainer, { 
            list: list,
            fontFamily: 'Inter, sans-serif',
            color: (word, weight) => (weight > 10 ? '#3B82F6' : (weight > 5 ? '#6B7280' : '#9CA3AF')),
            backgroundColor: 'transparent',
            shuffle: false,
            rotateRatio: 0,
            weightFactor: 4, // Làm cho các từ to hơn một chút
        });
    } else {
        wordCloudContainer.innerHTML = '<p style="text-align:center; color: var(--text-color-light);">Không đủ từ để tạo đám mây.</p>';
    }
}
});