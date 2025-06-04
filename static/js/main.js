document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('news-form');
    if (!form) return;

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const newsText = document.getElementById('news').value;

        fetch('/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ news: newsText })
        })
        .then(response => response.json())
        .then(data => {
            const resultContainer = document.createElement('section');
            resultContainer.innerHTML = `<h2>Detection Result:</h2><p>${data.prediction}</p>`;
            form.insertAdjacentElement('afterend', resultContainer);
        })
        .catch(error => {
            alert('An error occurred while analyzing news.');
            console.error(error);
        });
    });
});

