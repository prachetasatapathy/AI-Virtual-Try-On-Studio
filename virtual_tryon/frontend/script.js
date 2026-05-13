import { API_BASE_URL } from './firebase_config.js';

// DOM Elements
const authView = document.getElementById('auth-view');
const userView = document.getElementById('user-view');
const adminView = document.getElementById('admin-view');
const navbar = document.getElementById('navbar');
const userEmailDisplay = document.getElementById('user-email-display');

const authForm = document.getElementById('auth-form');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('login-btn');
const signupBtn = document.getElementById('signup-btn');
const logoutBtn = document.getElementById('logout-btn');
const authError = document.getElementById('auth-error');

const userPreviewArea = document.getElementById('user-preview-area');
const clothPreviewArea = document.getElementById('cloth-preview-area');
const userImageInput = document.getElementById('user-image');
const clothImageInput = document.getElementById('cloth-image');
const userPreview = document.getElementById('user-preview');
const clothPreview = document.getElementById('cloth-preview');
const tryOnBtn = document.getElementById('try-on-btn');
const btnText = document.querySelector('.btn-text');
const loader = document.getElementById('loader');
const resultSection = document.getElementById('result-section');
const resultImage = document.getElementById('result-image');
const resetBtn = document.getElementById('reset-btn');

const userHistoryGallery = document.getElementById('user-history-gallery');
const adminHistoryGallery = document.getElementById('admin-history-gallery');
const adminUsersTable = document.querySelector('#admin-users-table tbody');


const ADMIN_EMAIL = 'prachetasatapathy@gmail.com';


let userImageFile = null;
let clothImageFile = null;
let currentUser = null;
let currentToken = null;

// === Authentication Logic (MySQL REST) ===
function setUserSession(user, token) {
    currentUser = user;
    currentToken = token;
    userEmailDisplay.textContent = user.email;
    authView.style.display = 'none';
    navbar.style.display = 'flex';
    if (user.email === ADMIN_EMAIL) {
        userView.style.display = 'none';
        adminView.style.display = 'block';
        loadAdminData();
    } else {
        adminView.style.display = 'none';
        userView.style.display = 'block';
        loadUserHistory();
    }
}

function clearUserSession() {
    currentUser = null;
    currentToken = null;
    authView.style.display = 'flex';
    navbar.style.display = 'none';
    userView.style.display = 'none';
    adminView.style.display = 'none';
}

authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    authError.textContent = '';
    try {
        const email = emailInput.value;
        const password = passwordInput.value;
        if (!email || !password) throw new Error('Please enter email and password.');
        // Basic Auth header
        const token = btoa(`${email}:${password}`);
        // Try to get user info from backend
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { 'Authorization': `Basic ${token}` }
        });
        if (!response.ok) throw new Error('Invalid credentials');
        const user = await response.json();
        setUserSession(user, token);
    } catch (error) {
        authError.textContent = error.message;
    }
});

signupBtn.addEventListener('click', async () => {
    if (!emailInput.value || !passwordInput.value) {
        authError.textContent = 'Please enter email and password to sign up.';
        return;
    }
    authError.textContent = '';
    try {
        // Call backend to create user (implement /register endpoint in backend if needed)
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: emailInput.value, password: passwordInput.value })
        });
        if (!response.ok) throw new Error('Signup failed');
        alert('Signup successful! Please log in.');
    } catch (error) {
        authError.textContent = error.message;
    }
});

logoutBtn.addEventListener('click', clearUserSession);

// === Try-On Studio Logic ===

// Forward clicks to hidden inputs
userPreviewArea.addEventListener('click', () => userImageInput.click());
clothPreviewArea.addEventListener('click', () => clothImageInput.click());

// Handle file selections
userImageInput.addEventListener('change', (e) => handleFileSelect(e.target.files[0], 'user'));
clothImageInput.addEventListener('change', (e) => handleFileSelect(e.target.files[0], 'cloth'));

function handleFileSelect(file, type) {
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        if (type === 'user') {
            userImageFile = file;
            userPreview.src = e.target.result;
            userPreview.style.display = 'block';
            userPreviewArea.querySelector('.upload-placeholder').style.opacity = '0';
        } else {
            clothImageFile = file;
            clothPreview.src = e.target.result;
            clothPreview.style.display = 'block';
            clothPreviewArea.querySelector('.upload-placeholder').style.opacity = '0';
        }
        checkReadyState();
    };
    reader.readAsDataURL(file);
}

function checkReadyState() {
    if (userImageFile && clothImageFile) {
        tryOnBtn.disabled = false;
        tryOnBtn.style.animation = 'pulseBorder 2s infinite';
    } else {
        tryOnBtn.disabled = true;
        tryOnBtn.style.animation = 'none';
    }
}

resetBtn.addEventListener('click', () => {
    userImageFile = null;
    clothImageFile = null;
    userImageInput.value = '';
    clothImageInput.value = '';
    userPreview.style.display = 'none';
    clothPreview.style.display = 'none';
    document.querySelectorAll('.upload-placeholder').forEach(p => p.style.opacity = '1');
    resultSection.style.display = 'none';
    checkReadyState();
});


tryOnBtn.addEventListener('click', async () => {
    if (!currentUser || !currentToken) {
        alert("Please log in to use the Try-On feature.");
        return;
    }

    try {
        tryOnBtn.disabled = true;
        tryOnBtn.style.animation = 'none';
        btnText.textContent = 'Uploading Images...';
        loader.style.display = 'block';
        resultSection.style.display = 'none';

        if (!currentToken) {
            console.error("[DEBUG Frontend] Token is missing right before fetch!");
            throw new Error("Authentication token is missing. Please log in again.");
        }

        // Prepare FormData
        const formData = new FormData();
        formData.append('user_image', userImageFile);
        formData.append('cloth_image', clothImageFile);

        btnText.textContent = 'Weaving Magic...';
        console.log(`[DEBUG Frontend] Calling backend at ${API_BASE_URL}/try-on ...`);

        // 2. Call Backend API
        const response = await fetch(`${API_BASE_URL}/try-on`, {
            method: 'POST',
            headers: {
                'Authorization': `Basic ${currentToken}`
            },
            body: formData
        });

        if (!response.ok) {
            let errMessage = 'Backend API Try-On failed';
            try {
                const err = await response.json();
                console.error("Backend API Error:", err);
                errMessage = err.detail || errMessage;
            } catch (e) {
                console.error("Backend returned non-JSON error", response.status);
            }
            throw new Error(errMessage);
        }

        const data = await response.json();
        console.log("Backend response successful:", data);
        
        // 3. Display Result
        if (data.output_image) {
            resultImage.src = `http://127.0.0.1:8000/results/${data.output_image}`;
            resultImage.onload = () => {
                resultSection.style.display = 'block';
                resultSection.scrollIntoView({ behavior: 'smooth' });
            };
            alert("Try-On successful!");
        } else {
            alert("No output image returned.");
        }

        // Reload user history
        loadUserHistory();

    } catch (error) {
        console.error("Try-On Error Details:", error);
        alert("Error: " + error.message);
    } finally {
        tryOnBtn.disabled = false;
        btnText.textContent = 'Generate Try-On';
        loader.style.display = 'none';
        checkReadyState();
    }
});

// === History & Admin Logic ===

async function loadUserHistory() {
    if (!currentUser || !currentToken) return;
    try {
        // Fetch results for current user from backend
        const response = await fetch(`${API_BASE_URL}/user/history`, {
            headers: { 'Authorization': `Basic ${currentToken}` }
        });
        if (!response.ok) throw new Error('Failed to fetch user history');
        const data = await response.json();
        const history = data.history || [];
        userHistoryGallery.innerHTML = '';
        history.forEach(item => {
            const div = document.createElement('div');
            div.className = 'gallery-item';
            div.innerHTML = `<img src="${item.filename ? 'http://127.0.0.1:8000/results/' + item.filename : ''}" alt="Past Try-On" loading="lazy">`;
            userHistoryGallery.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading user history', error);
    }
}

async function loadAdminData() {
    if (!currentUser || !currentToken) return;
    try {
        const response = await fetch(`${API_BASE_URL}/admin/users`, {
            headers: { 'Authorization': `Basic ${currentToken}` }
        });
        if (!response.ok) throw new Error('Failed to fetch admin data');
        const data = await response.json();
        // Populate Users Table
        adminUsersTable.innerHTML = '';
        data.users.forEach(u => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${u.email}</td>
                <td>${u.tryon_count}</td>
                <td>${u.last_active ? new Date(u.last_active).toLocaleString() : ''}</td>
            `;
            adminUsersTable.appendChild(tr);
        });
        // Populate History Gallery
        adminHistoryGallery.innerHTML = '';
        data.history.forEach(item => {
            const div = document.createElement('div');
            div.className = 'gallery-item';
            div.innerHTML = `<img src="${item.filename ? 'http://127.0.0.1:8000/results/' + item.filename : ''}" alt="User Try-On" loading="lazy">`;
            adminHistoryGallery.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading admin data', error);
    }
}