import api from './axios';

export const authApi = {
  // Логин (передаем email и password)
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email); // FastAPI ожидает 'username' вместо 'email'
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data; // Вернет { access_token: "...", token_type: "bearer" }
  },

  // Регистрация (отправляем обычный JSON по адресу /users/)
  register: async (userData) => {
    const response = await api.post('/users/', userData);
    return response.data;
  },

  // Получение инфо о текущем юзере (для проверки токена)
  getMe: async () => {
    const response = await api.get('/auth/me'); // Если у тебя есть такой эндпоинт
    return response.data;
  }
};