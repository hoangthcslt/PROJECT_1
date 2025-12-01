// static/js/compare.js

document.addEventListener('DOMContentLoaded', () => {
    const urlA = document.getElementById('url-a');
    const urlB = document.getElementById('url-b');
    const compareBtn = document.getElementById('compare-btn');
    const resultSection = document.getElementById('result-section');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('error-message');
    const resultContent = document.getElementById('result-content');
    const recommendationContent = document.getElementById('ai-recommendation-content');
    const inputCard = document.querySelector('.compare-card'); // Lấy thẻ card chứa input
    // Chart variables
    let radarChart, barChart, trendChart;
    // Dark Mode (Copy từ script.js sang hoặc dùng chung 1 file util)
    // ... (Bạn có thể copy logic dark mode sang đây nếu muốn) ...

    compareBtn.addEventListener('click', async () => {
        const linkA = urlA.value.trim();
        const linkB = urlB.value.trim();

        if (!linkA || !linkB) {
            alert("Vui lòng nhập đủ link của 2 sản phẩm!");
            return;
        }

        // UI States
        resultSection.classList.remove('hidden');
        loader.classList.remove('hidden');
        errorMessage.classList.add('hidden');
        resultContent.classList.add('hidden');
        compareBtn.disabled = true;
        inputCard.classList.add('processing');
        compareBtn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Đang phân tích...'; // Thay đổi text nút
        try {
            const response = await fetch('/compare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ urls: [linkA, linkB], strategy: 'overview' })
            });

            const results = await response.json();

            // Kiểm tra lỗi từ backend
            if (results.some(r => r.error)) {
                throw new Error("Một trong các link sản phẩm không hợp lệ hoặc không thể cào dữ liệu.");
            }

            if (results.length < 2) throw new Error("Cần 2 sản phẩm để so sánh.");

            // Xử lý hiển thị
            displayComparison(results[0], results[1]);

            loader.classList.add('hidden');
            resultContent.classList.remove('hidden');
            // Scroll nhẹ xuống phần kết quả
            resultContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        } catch (error) {
            loader.classList.add('hidden');
            errorMessage.textContent = error.message;
            errorMessage.classList.remove('hidden');
        } finally {
            // === 2. TẮT HIỆU ỨNG LOADING (Dù thành công hay thất bại) ===
            loader.classList.add('hidden');
            inputCard.classList.remove('processing'); // Bỏ làm mờ
            compareBtn.disabled = false; // Mở khóa nút
            compareBtn.innerHTML = '<i class="ph ph-scales"></i> Phân tích & So sánh ngay'; 
        }
    });

    function displayComparison(prodA, prodB) {
        // 1. Hiển thị Header (Ảnh + Tên)
        document.getElementById('name-a').textContent = "Sản phẩm A (Xanh)"; // Nếu crawler có tên thì dùng prodA.product_info.name
        document.getElementById('name-b').textContent = "Sản phẩm B (Cam)";
        // Nếu crawler có ảnh: document.getElementById('img-a').src = prodA.product_info.image_url;
        // Xử lý hiển thị A
        const placeholderA = document.getElementById('placeholder-a');
        const imgA = document.getElementById('img-a');
        // Kiểm tra nếu có ảnh (giả sử backend trả về product_info.image_url)
        // Nếu chưa crawl được ảnh thì dùng ảnh mặc định hoặc giữ nguyên icon
        if (prodA.product_info && prodA.product_info.image_url) {
            imgA.src = prodA.product_info.image_url;
            placeholderA.classList.add('filled'); // Thêm class để hiện ảnh, ẩn icon
        }

        // Xử lý hiển thị B (tương tự)
        const placeholderB = document.getElementById('placeholder-b');
        const imgB = document.getElementById('img-b');
        if (prodB.product_info && prodB.product_info.image_url) {
            imgB.src = prodB.product_info.image_url;
            placeholderB.classList.add('filled');
        }
        // 2. Gọi Trợ lý ảo
        generateSmartAdvice(prodA, prodB);

        // 3. Vẽ Biểu đồ
        drawCompareRadar(prodA.radar_data, prodB.radar_data);
        drawCompareBar(prodA.stats, prodB.stats);
        drawCompareTrend(prodA.trend_data, prodB.trend_data);
    }

    // --- LOGIC TRỢ LÝ ẢO (PHẦN QUAN TRỌNG NHẤT) ---
    function generateSmartAdvice(a, b) {
        const scoreA = a.stats.positive;
        const scoreB = b.stats.positive;
        const diff = scoreA - scoreB;

        let html = `<p>Dựa trên dữ liệu từ người dùng thực tế:</p><ul style="line-height: 1.8;">`;

        // So sánh độ hài lòng
        if (diff > 5) {
            html += `<li>🏆 <strong>Sản phẩm A chiến thắng áp đảo</strong> về tỷ lệ hài lòng (${scoreA}% so với ${scoreB}%).</li>`;
        } else if (diff < -5) {
            html += `<li>🏆 <strong>Sản phẩm B chiến thắng áp đảo</strong> về tỷ lệ hài lòng (${scoreB}% so với ${scoreA}%).</li>`;
        } else {
            html += `<li>⚖️ <strong>Kẻ tám lạng, người nửa cân:</strong> Cả hai có độ hài lòng ngang ngửa nhau.</li>`;
        }

        // So sánh chi tiết (dựa trên Radar)
        const strongA = getStrongPoints(a.radar_data, b.radar_data);
        if (strongA.length > 0) {
            html += `<li>✅ <strong>Sản phẩm A</strong> vượt trội hơn về: <em>${strongA.join(', ')}</em>.</li>`;
        }

        const strongB = getStrongPoints(b.radar_data, a.radar_data);
        if (strongB.length > 0) {
            html += `<li>✅ <strong>Sản phẩm B</strong> vượt trội hơn về: <em>${strongB.join(', ')}</em>.</li>`;
        }

        // Kết luận
        html += `</ul><p style="margin-top:10px; font-weight:bold;">💡 Lời khuyên: </p>`;
        if (diff > 10) {
            html += `<p>Bạn nên chọn <strong>Sản phẩm A</strong> để có trải nghiệm an toàn nhất.</p>`;
        } else if (diff < -10) {
            html += `<p>Bạn nên chọn <strong>Sản phẩm B</strong> để có trải nghiệm an toàn nhất.</p>`;
        } else {
            html += `<p>Hãy cân nhắc yếu tố <strong>Giá cả</strong> và <strong>Mẫu mã</strong> (xem biểu đồ bên dưới) để quyết định, vì chất lượng hai bên khá tương đồng.</p>`;
        }

        recommendationContent.innerHTML = html;
    }

    function getStrongPoints(dataA, dataB) {
        let points = [];
        for (let key in dataA) {
            if (key !== 'Hài lòng' && (dataA[key] - dataB[key] > 10)) { // Hơn 10 điểm là vượt trội
                points.push(key);
            }
        }
        return points;
    }

    // --- CÁC HÀM VẼ BIỂU ĐỒ (CHART.JS) ---

       function drawCompareRadar(dataA, dataB) {
        if (radarChart) radarChart.destroy();
        const ctx = document.getElementById('compare-radar-chart');

        radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.keys(dataA),
                datasets: [
                    {
                        label: 'Sản phẩm A',
                        data: Object.values(dataA),
                        borderColor: '#0e56caff',
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    },
                    {
                        label: 'Sản phẩm B',
                        data: Object.values(dataB),
                        borderColor: '#F59E0B',
                        backgroundColor: 'rgba(245, 158, 11, 0.2)',
                    }
                ]
            },
            options: {
                scales: { 
                    r: { 
                        grid: {
                            color: 'rgba(20, 204, 218, 0.2)'
                        },
                        // Màu các đường kẻ hướng tâm
                        angleLines: {
                            display: true,
                            color: 'rgba(20, 204, 218, 0.2)'
                        },
                        suggestedMin: 0, 
                        suggestedMax: 100,
                        ticks: {
                            stepSize: 50, 
                            backdropColor: 'transparent', // Xóa cái nền trắng đè lên chữ
                            color: '#1ddc16ff', // Màu số nhạt hơn cho tinh tế
                            font: {
                                size: 10
                            }
                        }
                    } 
                }
            }
        });
    }

    function drawCompareBar(statsA, statsB) {
        if (barChart) barChart.destroy();
        const ctx = document.getElementById('compare-bar-chart');

        barChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Hài lòng', 'Bình thường', 'Không hài lòng'],
                datasets: [
                    {
                        label: 'Sản phẩm A',
                        data: [statsA.positive, statsA.neutral, statsA.negative],
                        backgroundColor: '#3B82F6'
                    },
                    {
                        label: 'Sản phẩm B',
                        data: [statsB.positive, statsB.neutral, statsB.negative],
                        backgroundColor: '#F59E0B'
                    }
                ]
            },
            options: {
                scales: { y: { beginAtZero: true, max: 100 } }
            }
        });
    }

    function drawCompareTrend(trendA, trendB) {
        if (trendChart) trendChart.destroy();
        const ctx = document.getElementById('compare-trend-chart');

        // Cần gộp labels của cả 2 để trục thời gian đúng
        // (Ở đây làm đơn giản: dùng labels của A, thực tế cần merge và sort lại)
        const labels = trendA.labels.length > trendB.labels.length ? trendA.labels : trendB.labels;

        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Xu hướng A',
                        data: trendA.values,
                        borderColor: '#3B82F6',
                        tension: 0.4
                    },
                    {
                        label: 'Xu hướng B',
                        data: trendB.values,
                        borderColor: '#F59E0B',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
});