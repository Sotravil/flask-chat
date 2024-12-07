document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');
    const registerContainer = document.getElementById('register-container');
    const loginContainer = document.getElementById('login-container');
    const registerMessage = document.getElementById('register-message');
    const loginMessage = document.getElementById('login-message');
    const toggleToLogin = document.getElementById('toggle-to-login');
    const toggleToRegister = document.getElementById('toggle-to-register');

    // Toggle to login form
    if (toggleToLogin) {
        toggleToLogin.addEventListener('click', (e) => {
            e.preventDefault();
            registerContainer.style.display = 'none';
            loginContainer.style.display = 'block';
            clearMessages();
        });
    }

    // Toggle to register form
    if (toggleToRegister) {
        toggleToRegister.addEventListener('click', (e) => {
            e.preventDefault();
            loginContainer.style.display = 'none';
            registerContainer.style.display = 'block';
            clearMessages();
        });
    }

    // Handle registration form submission
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('register-username').value;
            const password = document.getElementById('register-password').value;

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                });

                const result = await response.json();
                registerMessage.textContent = result.message;

                if (result.status === 'error') {
                    // Suggest logging in if user already exists
                    registerMessage.textContent = 'User already exists. Redirecting to login...';
                    setTimeout(() => toggleToLogin.click(), 2000);
                }
            } catch (error) {
                registerMessage.textContent = 'An error occurred during registration. Please try again.';
                console.error('Registration Error:', error);
            }
        });
    }

    // Handle login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                });

                const result = await response.json();
                loginMessage.textContent = result.message;

                if (result.status === 'success') {
                    // Redirect to home on successful login
                    window.location.href = '/home';
                }
            } catch (error) {
                loginMessage.textContent = 'An error occurred during login. Please try again.';
                console.error('Login Error:', error);
            }
        });
    }

    // Clear messages
    function clearMessages() {
        if (registerMessage) registerMessage.textContent = '';
        if (loginMessage) loginMessage.textContent = '';
    }
});
