document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const csrfToken = document.getElementById("csrf_token").value;
        const loginData = {
            email: document.getElementById("email").value,
            password: document.getElementById("password").value
        };


      fetch('/submit-login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
         credentials: 'same-origin',
        'X-CSRFToken': document.getElementById("csrf_token").value
    },
    body: JSON.stringify(loginData)
})
.then(response => {
    if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
    }
    return response.json();
})
.then(data => {
    if (data.success) {
        window.location.href = data.redirect;
    } else {
        alert('Login failed: ' + data.message);
    }
})
.catch(error => {
    console.error('Error:', error);
    alert('An error occurred. Please try again later.');
});
    });
});