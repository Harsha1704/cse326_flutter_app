const wrapper = document.querySelector('.wrapper');
const loginLink = document.querySelector('.login-link');
const registerLink = document.querySelector('.register-link');
const btnPopup = document.querySelector('.btnLogin-popup');
const loginForm = document.querySelector('.login form'); 
const registerForm = document.querySelector('.register form'); 
const loginButton = document.querySelector('.btn'); 
const emailInput = document.querySelector('input[name="email"]'); 
const passwordInput = document.querySelector('input[name="pass"]'); 
const menuIcon = document.querySelector('.menu-toggle');
const nav = document.querySelector('.navigation');

// By default show login
wrapper.classList.add('active-popup');
wrapper.classList.remove('active');

// Show register form
registerLink.addEventListener('click', () => {
    wrapper.classList.add('active');
});

// Switch back to login form
loginLink.addEventListener('click', () => {
    wrapper.classList.remove('active');
});

// Open login form when login clicked from nav
btnPopup.addEventListener('click', () => {
    wrapper.classList.add('active-popup');
    wrapper.classList.remove('active'); // force login tab
    nav.classList.remove('active');     // close sidebar
});

// Sidebar toggle
menuIcon.addEventListener('click', () => {
    nav.classList.toggle('active');
});

// Login check - calls the real Flask backend
loginButton.addEventListener("click", function(e) {
    e.preventDefault();

    const emailid = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const errorBox = document.getElementById('login-error');
    errorBox.textContent = '';

    if (!emailid || !password) {
        errorBox.textContent = "Please enter both email and password.";
        return;
    }

    fetch(`${window.API_BASE_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailid, password: password })
    })
        .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            if (!ok) {
                errorBox.textContent = data.error || "Login failed.";
                return;
            }
            localStorage.setItem('authToken', data.token);
            localStorage.setItem('userEmail', data.email);
            localStorage.setItem('userName', data.name || '');
            window.location.href = "main_page.html";
        })
        .catch(() => {
            errorBox.textContent = "Could not reach the server. Is the backend running?";
        });
});

// On register submit - creates a real account via the Flask backend
registerForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const username = document.querySelector('input[name="username"]').value.trim();
    const regEmail = document.querySelector('input[name="reg-email"]').value.trim();
    const regPass = document.querySelector('input[name="reg-pass"]').value.trim();
    const errorBox = document.getElementById('register-error');
    errorBox.textContent = '';

    if (!username || !regEmail || !regPass) {
        errorBox.textContent = "Please fill in all fields.";
        return;
    }

    fetch(`${window.API_BASE_URL}/api/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: username, email: regEmail, password: regPass })
    })
        .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            if (!ok) {
                errorBox.textContent = data.error || "Registration failed.";
                return;
            }
            localStorage.setItem('authToken', data.token);
            localStorage.setItem('userEmail', data.email);
            localStorage.setItem('userName', data.name || '');
            window.location.href = "main_page.html";
        })
        .catch(() => {
            errorBox.textContent = "Could not reach the server. Is the backend running?";
        });
});