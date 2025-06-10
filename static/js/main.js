document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('news-form');
    if (!form) return;

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const newsText = document.getElementById('news').value.trim();

        if (!newsText) {
            alert('Please enter a news link or text.');
            return;
        }

        // Remove previous result if it exists
        const oldResult = document.getElementById('detection-result');
        if (oldResult) oldResult.remove();

        fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ news: newsText })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Server response:", data);

            const resultContainer = document.createElement('section');
            resultContainer.id = 'detection-result';

            if (data.error) {
                resultContainer.innerHTML = `<h2>Error:</h2><p>${data.error}</p>`;
            } else {
                resultContainer.innerHTML = `<h2>Detection Result:</h2><p>${data.prediction}</p>`;
            }

            form.insertAdjacentElement('afterend', resultContainer);
        })
        .catch(error => {
            console.error("Fetch error:", error);
            alert('An error occurred while analyzing news.');
        });
    });
});