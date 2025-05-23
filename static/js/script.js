document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(loginForm);
        const data = {
          email: document.getElementById("email").value,
          password: document.getElementById("password").value
    };



        const csrfToken = document.getElementById("csrf_token").value;

        fetch('/submit-login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken  // ✅ Include CSRF token properly
    },
    body: JSON.stringify(data)  // ✅ Use the data object


})
.then(response => response.json())
.then(data => {
    if (data.success) {
        window.location.href = data.redirect;  // ✅ Use Flask's redirect
    } else {
        alert('Login failed: ' + data.message);
    }
});
    });
});