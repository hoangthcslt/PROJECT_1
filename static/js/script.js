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
    const wordCloudContainer = document.getElementById('wordcloud-container');
    const reviewsList = document.getElementById('reviews-list');
    const chartCanvas = document.getElementById('sentiment-chart');
    const wordCloudPositiveContainer = document.getElementById('wordcloud-positive-container');
    const wordCloudNegativeContainer = document.getElementById('wordcloud-negative-container');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const showAllBtn = document.getElementById('show-all-btn');
    const tabButtons = document.querySelectorAll('.tab-button');
    const strategyButtons = document.querySelectorAll('.strategy-btn');

    let sentimentChart = null; // Biến lưu trữ biểu đồ
    let allReviewsData = []; // Biến LƯU TRỮ TOÀN BỘ bình luận
    // Biến để lưu chiến lược đang được chọn
    let currentStrategy = 'latest';
    // === Thêm logic xử lý chọn chiến lược ===
    strategyButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Xóa class 'active' khỏi tất cả các nút
            strategyButtons.forEach(btn => btn.classList.remove('active'));
            // Thêm class 'active' cho nút vừa được click
            button.classList.add('active');
            // Cập nhật biến chiến lược
            currentStrategy = button.dataset.strategy;
        });
    });
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
            // Gửi yêu cầu đến API
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    strategy: currentStrategy
                }),
            });
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Có lỗi xảy ra.');
            }

            // LƯU TRỮ dữ liệu gốc
            allReviewsData = result.reviews || [];

            //Hiển thị kết quả
            //Thêm độ trễ để thấy hiệu ứng
            setTimeout(() => {
                hideElement(skeletonLoader);
                displayResults(result); // Gọi hàm hiển thị chính
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
        //Chart
        drawChart(data.stats);

        //***** */
        displayReviews(allReviewsData); // Luôn hiển thị TẤT CẢ lúc đầu
        drawWordClouds(allReviewsData); // Vẽ word cloud từ dữ liệu gốc
        //***** */  

    }

    // NÂNG CẤP: Hàm displayReviews giờ có thể nhận một danh sách bất kỳ
    function displayReviews(reviews) {
        reviewsList.innerHTML = '';
        if (reviews && reviews.length > 0) {
            reviews.forEach(review => {
                //Tạo element review
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
            reviewsList.innerHTML = '<p style="text-align:center; color: var(--text-color-light);">Không có bình luận nào phù hợp.</p>';
        }
    }

    // NÂNG CẤP: Logic cho Biểu đồ tương tác
    function drawChart(stats) {
        if (sentimentChart) sentimentChart.destroy();
        const chartData = {
            labels: ['Hài lòng', 'Bình thường', 'Không hài lòng'],
            datasets: [{
                data: [stats.positive, stats.neutral, stats.negative],
                backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
                borderWidth: 0,
            }]
        };

        sentimentChart = new Chart(chartCanvas, {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: { legend: { display: false } },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const clickedIndex = elements[0].index;
                        const sentimentMap = ['tích cực', 'trung tính', 'tiêu cực'];
                        const targetSentiment = sentimentMap[clickedIndex];

                        // Lọc và hiển thị lại danh sách bình luận
                        const filteredReviews = allReviewsData.filter(r => r.sentiment === targetSentiment);
                        displayReviews(filteredReviews);
                        showElement(showAllBtn); // Hiện nút "Hiển thị tất cả"
                    }
                }
            }
        });
    }

    // NÚT HIỂN THỊ TẤT CẢ
    showAllBtn.addEventListener('click', () => {
        displayReviews(allReviewsData);
        hideElement(showAllBtn);
    });

    // NÂNG CẤP: Logic cho Word Cloud thông minh hơn
    function drawWordClouds(reviews) {
        const positiveReviews = reviews.filter(r => r.sentiment === 'tích cực');
        const negativeReviews = reviews.filter(r => r.sentiment === 'tiêu cực');

        // Stop words tốt hơn, không loại bỏ các từ quan trọng
        const stopWords = ['bị', 'bởi', 'cả', 'các', 'cái', 'cần', 'càng', 'chỉ', 'chiếc', 'cho', 'chứ', 'chưa', 'chuyện', 'có', 'có_thể', 'cứ', 'của', 'cùng', 'cũng', 'đã', 'đang', 'đây', 'để', 'đến', 'đều', 'điều', 'do', 'đó', 'được', 'gì', 'khi', 'không', 'là', 'lại', 'lên', 'lúc', 'mà', 'mỗi', 'một', 'nên', 'nếu', 'ngay', 'nhiều', 'như', 'nhưng', 'những', 'nơi', 'nữa', 'phải', 'qua', 'ra', 'rằng', 'rất', 'rồi', 'sau', 'sẽ', 'so', 'sự', 'tại', 'theo', 'thì', 'trên', 'trước', 'từ', 'từng', 'và', 'vẫn', 'vào', 'vậy', 'vì', 'việc', 'với'];

        const generateWordList = (reviewList) => {
            const text = reviewList.map(r => r.comment || '').join(' ').toLowerCase();
            const words = text.split(/[ \n\r\t.,!?"();:]+/).filter(word => {
                return word.length > 2 && !stopWords.includes(word) && isNaN(word);
            });
            const frequencies = words.reduce((map, word) => {
                map[word] = (map[word] || 0) + 1; return map;
            }, {});
            return Object.entries(frequencies).sort((a, b) => b[1] - a[1]).slice(0, 50);
        };

        const positiveList = generateWordList(positiveReviews);
        const negativeList = generateWordList(negativeReviews);

        const cloudOptions = {
            fontFamily: 'Inter, sans-serif',
            backgroundColor: 'transparent',
            shuffle: false,
            rotateRatio: 0,
            minSize: 10
        };

        if (positiveList.length > 5) {
            WordCloud(wordCloudPositiveContainer, { ...cloudOptions, list: positiveList, color: '#10B981' });
        } else {
            wordCloudPositiveContainer.innerHTML = '<p style="text-align:center; color: var(--text-color-light);">Không đủ dữ liệu.</p>';
        }
        if (negativeList.length > 5) {
            WordCloud(wordCloudNegativeContainer, { ...cloudOptions, list: negativeList, color: '#EF4444' });
        } else {
            wordCloudNegativeContainer.innerHTML = '<p style="text-align:center; color: var(--text-color-light);">Không đủ dữ liệu.</p>';
        }
    }

    // LOGIC CHO TABS CỦA WORD CLOUD
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            if (button.dataset.type === 'positive') {
                showElement(wordCloudPositiveContainer);
                hideElement(wordCloudNegativeContainer);
            } else {
                hideElement(wordCloudPositiveContainer);
                showElement(wordCloudNegativeContainer);
            }
        });
    });
});