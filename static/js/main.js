document.addEventListener('DOMContentLoaded', () => {
    const predictionForm = document.getElementById('predictionForm');
    const resultSection = document.getElementById('resultSection');

    predictionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // 显示加载状态
        showLoading();

        // 收集表单数据
        const formData = {
            name: document.getElementById('name').value,
            birthDate: document.getElementById('birthDate').value,
            gender: document.getElementById('gender').value,
            birthPlace: document.getElementById('birthPlace').value
        };

        try {
            // 发送预测请求
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('预测请求失败');
            }

            const predictionResult = await response.json();
            displayPrediction(predictionResult);
        } catch (error) {
            showError(error.message);
        } finally {
            hideLoading();
        }
    });

    function displayPrediction(result) {
        // 显示结果区域
        resultSection.style.display = 'grid';

        // 更新2024年预测
        document.getElementById('events2024').textContent = result.prediction2024.events;
        document.getElementById('attention2024').textContent = result.prediction2024.attention;

        // 更新2025年预测
        document.getElementById('events2025').textContent = result.prediction2025.events;
        document.getElementById('attention2025').textContent = result.prediction2025.attention;

        // 更新文化解读
        document.getElementById('culturalInterpretation').textContent = result.culturalInterpretation;

        // 平滑滚动到结果区域
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    function showLoading() {
        const submitBtn = document.querySelector('.submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = '正在生成预测...';
        submitBtn.style.opacity = '0.7';
    }

    function hideLoading() {
        const submitBtn = document.querySelector('.submit-btn');
        submitBtn.disabled = false;
        submitBtn.textContent = '生成预测';
        submitBtn.style.opacity = '1';
    }

    function showError(message) {
        alert(`错误：${message}`);
    }
});
