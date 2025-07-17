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

// Login check
loginButton.addEventListener("click", function(e) {
    e.preventDefault();

    const emailid = emailInput.value.trim(); 
    const password = passwordInput.value.trim(); 

    if (!emailid || !password) {
        alert("Please enter both email and password.");
        return;
    }

    if (emailid === "abc@gmail.com" && password === "123456") {
        window.location.href = "main_page.html";
    } else {
        alert("Invalid email or password.");
    }
});

// On register submit
registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
    window.location.href = "main_page.html";
});
