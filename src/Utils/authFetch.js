export async function authFetch(url, options = {}) {
  const token = localStorage.getItem('token');

  const headers = {
    ...options.headers,
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Optional: logout on 401
  if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/'; 
  }

  return response;
}
