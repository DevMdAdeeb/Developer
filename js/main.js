document.addEventListener('DOMContentLoaded', function() {
    // Get modal elements
    const modal = document.getElementById('auth-modal');
    const authButton = document.getElementById('auth-button');
    const closeButton = document.querySelector('.close-button');

    // Forms and links
    const loginContainer = document.getElementById('login-form-container');
    const signupContainer = document.getElementById('signup-form-container');
    const showSignupLink = document.getElementById('show-signup');
    const showLoginLink = document.getElementById('show-login');

    // Open modal
    if (authButton) {
        authButton.addEventListener('click', function() {
            modal.style.display = 'block';
        });
    }

    // Close modal
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }

    // Close modal if user clicks outside of it
    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });

    // Switch to signup form
    if (showSignupLink) {
        showSignupLink.addEventListener('click', function(e) {
            e.preventDefault();
            loginContainer.style.display = 'none';
            signupContainer.style.display = 'block';
        });
    }

    // Switch to login form
    if (showLoginLink) {
        showLoginLink.addEventListener('click', function(e) {
            e.preventDefault();
            signupContainer.style.display = 'none';
            loginContainer.style.display = 'block';
        });
    }

    // Helper function to display messages
    function showMessage(formElement, message, isSuccess) {
        const messageContainer = formElement.querySelector('.message-container');
        messageContainer.textContent = message;
        messageContainer.className = 'message-container'; // Reset classes
        if (isSuccess) {
            messageContainer.classList.add('success');
        } else {
            messageContainer.classList.add('error');
        }
    }

    // Handle Signup Form Submission
    const signupForm = document.getElementById('signup-form');
    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('includes/handle_signup.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            showMessage(this, data.message, data.success);
            if (data.success) {
                setTimeout(() => {
                    modal.style.display = 'none';
                    showLoginLink.click();
                }, 1500); // Wait 1.5s before closing
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage(this, 'حدث خطأ أثناء الاتصال بالخادم.', false);
        });
    });

    // Handle Login Form Submission
    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('includes/handle_login.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            showMessage(this, data.message, data.success);
            if (data.success) {
                setTimeout(() => {
                    modal.style.display = 'none';
                    document.getElementById('auth-button').textContent = `مرحباً، ${data.user.name}`;
                    // Optionally, reload the page to reflect logged-in state everywhere
                    // window.location.reload();
                }, 1500);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage(this, 'حدث خطأ أثناء الاتصال بالخادم.', false);
        });
    });
});
