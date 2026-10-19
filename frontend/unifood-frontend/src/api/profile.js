import api from './axios';

export const profileApi = {
  // Получить информацию о текущем пользователе
  getProfile: async () => {
    const response = await api.get('/profile/me');
    return response.data;
  },

  // Обновить информацию о пользователе
  updateProfile: async (userData) => {
    const response = await api.put('/profile/me', userData);
    return response.data;
  },

  // Пополнить баланс
  addBalance: async (amount) => {
    const response = await api.post('/profile/balance', { amount });
    return response.data;
  },

  // Получить текущий баланс
  getBalance: async () => {
    const response = await api.get('/profile/balance');
    return response.data;
  }
};
