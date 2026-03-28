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
    
    const response = await fetch(API_BASE + url, {
        ...options,
        headers
    });
    
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
