document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form[action="/predict"]');
    if (!form) return;

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        const newsText = document.getElementById('news').value;

        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ news: newsText })
        })
        .then(response => response.text())
        .then(html => {
            // Replace the main content with the new HTML (or just update the result section)
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const resultSection = doc.querySelector('section');
            if (resultSection) {
                const currentResult = document.querySelector('section');
                if (currentResult) {
                    currentResult.replaceWith(resultSection);
                } else {
                    form.insertAdjacentElement('afterend', resultSection);
                }
            }
        })
        .catch(error => {
            alert('An error occurred while detecting news.');
            console.error(error);
        });
    });
});