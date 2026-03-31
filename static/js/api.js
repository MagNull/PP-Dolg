// базовый URL — тот же origin
const API_BASE = "";

// получаем токен из localStorage
function getToken() {
    return localStorage.getItem("token");
}

// сохраняем токен
function saveToken(token) {
    localStorage.setItem("token", token);
}

// удаляем токен
function removeToken() {
    localStorage.removeItem("token");
}

// основная функция для запросов к API
async function apiRequest(url, options = {}) {
    const token = getToken();
    const headers = {
        "Content-Type": "application/json",
        ...options.headers
    };
    
    // добавляем токен если есть
    if (token) {
        headers["Authorization"] = "Bearer " + token;
    }
    
    // если передан body как FormData или URLSearchParams — убираем Content-Type
    // это нужно для /api/auth/login которая ожидает form-urlencoded
    if (options.body instanceof URLSearchParams || options.body instanceof FormData) {
        delete headers["Content-Type"];
    }
    
    console.log("[API]", options.method || "GET", url);

    const response = await fetch(API_BASE + url, {
        ...options,
        headers
    });
    
    console.log("[API]", response.status, url);

    return response;
}

// проверяем залогинен ли пользователь
function isLoggedIn() {
    return !!getToken();
}

// получаем данные текущего пользователя
async function getCurrentUser() {
    const response = await apiRequest("/api/auth/me");
    if (response.ok) {
        return await response.json();
    }
    return null;
}

// выход — удаляем токен и редиректим на login
function logout() {
    removeToken();
    window.location.href = "/login.html";
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text ?? "";
    return div.innerHTML;
}

// русские названия типов занятости
function employmentTypeLabel(type) {
    var labels = {
        'part_time': 'Частичная занятость',
        'full_time': 'Полная занятость',
        'internship': 'Стажировка'
    };
    return labels[type] || type;
}

function applicationStatusClass(statusId) {
    var classes = {
        1: 'warning text-dark',
        2: 'info text-dark',
        3: 'success',
        4: 'danger'
    };
    return classes[statusId] || 'secondary';
}

function applicationStatusText(statusId, statusName) {
    if (statusId === 3) return 'Одобрено';
    if (statusId === 4) return 'Отказ';
    if (statusId === 2) return 'Просмотрено';
    return statusName || 'Отклик отправлен';
}
