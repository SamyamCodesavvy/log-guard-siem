const TOKEN_KEY = 'loggard_token';
const USER_KEY = 'loggard_user';

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = '/ui/login';
  }
}

// Wrapper around fetch that injects the Bearer token and
// redirects to login on 401 (expired/invalid token)
async function authFetch(url, options = {}) {
  const token = getToken();
  const headers = {
    ...(options.headers || {}),
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) {
    clearSession();
    window.location.href = '/ui/login';
    throw new Error('Session expired');
  }
  return res;
}

function logout() {
  clearSession();
  window.location.href = '/ui/login';
}

function currentUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY));
  } catch {
    return null;
  }
}