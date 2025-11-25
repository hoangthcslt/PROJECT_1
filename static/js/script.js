/*
ĐÂY LÀ FILE QUẢN LÝ LOGIC
*/
document.addEventListener('DOMContentLoaded', () => {
    // === Lấy các element từ HTML ===
    const radarCanvas = document.getElementById('radar-chart');
    const trendCanvas = document.getElementById('trend-chart');
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
    let radarChart = null;
    let trendChart = null;
    let allReviewsData = []; // Biến LƯU TRỮ TOÀN BỘ bình luận
    // Biến để lưu phương án phân tích 
    let currentStrategy = 'latest';
    // === logic xử lý khi chọn cách phân tích ===
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

    // === Logic cho Dark Mode ( chế độ tối ) ===
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

        // Chuẩn bị giao diện
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
            //Thêm độ trễ
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


    // === Các hàm hiển thị trên giao diện ===
    function displayResults(data) {
        // TỔNG QUAN CÁC ĐÁNH GIÁ
        statsSummary.innerHTML = `
            <p><strong>Tổng số đánh giá:</strong> ${data.stats.total_reviews}</p>
            <p><i class="ph ph-smiley" style="color:var(--green-color)"></i><strong>Hài lòng:</strong> ${data.stats.positive}%</p>
            <p><i class="ph ph-smiley-meh" style="color:var(--yellow-color)"></i><strong>Bình thường:</strong> ${data.stats.neutral}%</p>
            <p><i class="ph ph-smiley-sad" style="color:var(--red-color)"></i><strong>Không hài lòng:</strong> ${data.stats.negative}%</p>
        `;
        //Chart
        drawRadarChart(data.radar_data); // <--- GỌI HÀM MỚI
        drawTrendChart(data.trend_data); // <--- GỌI HÀM MỚI
        displayAttributeSummary(data.attribute_summary);
        drawChart(data.stats);
        displayReviews(allReviewsData); // Luôn hiển thị TẤT CẢ lúc đầu
    }

    function displayReviews(reviews) { //Hiển thị các đánh giá bên dưới 1 cách trực quan hơn 
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

    // Logic cho Biểu đồ hiển thị tỉ lệ đánh giá để user có thể tương tác
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
                        showElement(showAllBtn); // Hiện "Hiển thị tất cả"
                    }
                }
            }
        });
    }

    showAllBtn.addEventListener('click', () => {
        displayReviews(allReviewsData);
        hideElement(showAllBtn);
    });
    //  === VIẾT HÀM VẼ RADAR CHART ===
    function drawRadarChart(radarData) {
        if (radarChart) radarChart.destroy();

        // Radar data là object: {"Hài lòng": 90, "Giá cả": 50...}
        const labels = Object.keys(radarData);
        const values = Object.values(radarData);

        radarChart = new Chart(radarCanvas, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Điểm số',
                    data: values,
                    fill: true,
                    backgroundColor: 'rgba(59, 130, 246, 0.2)', // Màu xanh nhạt
                    borderColor: '#3B82F6', // Màu xanh đậm
                    borderWidth: 2,
                    pointBackgroundColor: '#3B82F6',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#3B82F6'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        grid: {
                            color: 'rgba(156, 163, 175, 0.2)'
                        },
                        // Màu các đường kẻ hướng tâm
                        angleLines: {
                            display: true,
                            color: 'rgba(156, 163, 175, 0.2)'
                        },
                        // Cấu hình thang đo (0 - 100)
                        suggestedMin: 0,
                        suggestedMax: 100,

                        // === PHẦN QUAN TRỌNG ĐỂ SỬA LỖI HIỂN THỊ ===
                        ticks: {
                            stepSize: 50, // Chỉ hiện mốc 0, 50, 100 cho đỡ rối
                            backdropColor: 'transparent', // Xóa cái nền trắng đè lên chữ
                            color: '#1ddc16ff', // Màu số nhạt hơn cho tinh tế
                            font: {
                                size: 12
                            }
                        },
                        // Cấu hình nhãn các trục (Hài lòng, Giá cả...)
                        pointLabels: {
                            font: {
                                size: 12,
                                family: "'Inter', sans-serif",
                                weight: '500'
                            },
                            color: '#E5E7EB' // Màu chữ sáng để nổi trên nền tối
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => ` ${context.label}: ${context.raw}/100 điểm`
                        }
                    }
                }
            }
        });
    }
    // 5. === VIẾT HÀM VẼ TREND CHART ===
    function drawTrendChart(trendData) {
        if (trendChart) trendChart.destroy();

        // trendData: {labels: ["2023-01", ...], values: [4.5, ...]}
        if (!trendData || trendData.labels.length === 0) {
            // Xử lý trường hợp không có dữ liệu xu hướng
            return;
        }

        trendChart = new Chart(trendCanvas, {
            type: 'line',
            data: {
                labels: trendData.labels,
                datasets: [{
                    label: 'Sao trung bình',
                    data: trendData.values,
                    borderColor: '#10B981', // Màu xanh lá
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    tension: 0.4, // Làm mượt đường kẻ
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 1,
                        max: 5, // Thang điểm sao từ 1 đến 5
                        ticks: { stepSize: 1 }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => `Trung bình: ${context.raw} sao`
                        }
                    }
                }
            }
        });
    }
    function displayAttributeSummary(summary) {
        // 1. Lấy thẻ div chứa nội dung tóm tắt
        const aiSummaryContainer = document.getElementById('ai-summary-container');

        // 2. Xóa nội dung cũ (để tránh bị trùng lặp khi bấm Phân tích nhiều lần)
        aiSummaryContainer.innerHTML = '';

        // 3. Kiểm tra dữ liệu đầu vào
        // 'summary' là object attribute_vote_summary từ API
        // 'summary.votes' là mảng chứa các khía cạnh (ví dụ: {name: "đẹp", agree: 10, disagree: 1})
        const votes = summary ? summary.votes : [];

        if (!votes || votes.length === 0) {
            // Nếu không có dữ liệu, hiện thông báo trống
            aiSummaryContainer.innerHTML = '<p class="placeholder-text" style="text-align:center; color:#888">Chưa có dữ liệu tóm tắt từ người dùng.</p>';
            return;
        }

        // 4. Logic Lọc và Sắp xếp (QUAN TRỌNG NHẤT)

        // --- Lọc ĐIỂM CỘNG (Pros) ---
        const pros = votes
            .filter(v => v.agree > v.disagree) // Điều kiện 1: Số người khen phải nhiều hơn chê
            .filter(v => v.agree > 0)          // Điều kiện 2: Phải có ít nhất 1 người khen (để lọc nhiễu)
            .sort((a, b) => b.agree - a.agree); // Sắp xếp: Cái nào được khen nhiều nhất lên đầu

        // --- Lọc ĐIỂM TRỪ (Cons) ---
        const cons = votes
            .filter(v => v.disagree > v.agree) // Điều kiện 1: Số người chê nhiều hơn khen
            .filter(v => v.disagree > 0)       // Điều kiện 2: Phải có ít nhất 1 người chê
            .sort((a, b) => b.disagree - a.disagree); // Sắp xếp: Cái nào bị chê nhiều nhất lên đầu

        // 5. Tạo chuỗi HTML để hiển thị
        let html = '';

        // Nếu có điểm cộng
        if (pros.length > 0) {
            // Thêm tiêu đề màu xanh lá
            html += `<h5 style="color: #10B981; font-weight:bold; margin-bottom:5px; display:flex; align-items:center; gap:5px;">
                    <i class="ph ph-thumbs-up"></i> Điểm cộng
                 </h5>`;
            html += `<ul style="margin-top:0; padding-left:20px;">`;

            // Chỉ lấy tối đa 5 điểm cộng nổi bật nhất (.slice(0, 5))
            pros.slice(0, 5).forEach(item => {
                html += `<li style="margin-bottom:4px; color:#4B5563;">
                        ${item.attribute_name} 
                        <span style="font-size:0.8em; color:#9CA3AF;">(${item.agree} đồng ý)</span>
                     </li>`;
            });
            html += `</ul>`;
        }

        // Nếu có điểm trừ
        if (cons.length > 0) {
            // Thêm khoảng cách nếu đã có điểm cộng ở trên
            const marginTop = pros.length > 0 ? 'margin-top: 15px;' : '';

            // Thêm tiêu đề màu đỏ
            html += `<h5 style="color: #EF4444; font-weight:bold; margin-bottom:5px; ${marginTop} display:flex; align-items:center; gap:5px;">
                    <i class="ph ph-thumbs-down"></i> Điểm trừ
                 </h5>`;
            html += `<ul style="margin-top:0; padding-left:20px;">`;

            // Chỉ lấy tối đa 5 điểm trừ nổi bật nhất
            cons.slice(0, 5).forEach(item => {
                html += `<li style="margin-bottom:4px; color:#4B5563;">
                        ${item.attribute_name} 
                        <span style="font-size:0.8em; color:#9CA3AF;">(${item.disagree} đồng ý)</span>
                     </li>`;
            });
            html += `</ul>`;
        }

        // 6. Đưa HTML đã tạo vào giao diện
        if (html === '') {
            aiSummaryContainer.innerHTML = '<p class="placeholder-text">Dữ liệu chưa đủ để kết luận ưu/nhược điểm.</p>';
        } else {
            aiSummaryContainer.innerHTML = html;
        }
    }
    // LOGIC CHO TABS WORD CLOUD
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