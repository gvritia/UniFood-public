import api from './axios';

export const menuApi = {
  // Получить всё меню (с опциональными фильтрами)
  getMenu: async (params = {}) => {
    const response = await api.get('/menu/', { params });
    return response.data;
  },

  // Получить одно блюдо по ID
  getItem: async (id) => {
    const response = await api.get(`/menu/${id}`);
    return response.data;
  }
};