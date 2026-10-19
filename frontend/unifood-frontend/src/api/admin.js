import api from './axios';

export const adminApi = {
  // Получить общую статистику
  getStats: async () => {
    const response = await api.get('/admin/stats');
    return response.data;
  },

  // Получить список всех заказов
  getOrders: async (params = {}) => {
    const response = await api.get('/admin/orders', { params });
    return response.data;
  },

  // Обновить статус заказа
  updateOrderStatus: async (orderId, status) => {
    const response = await api.patch(`/admin/orders/${orderId}/status`, { status });
    return response.data;
  },

  // Получить всех пользователей
  getUsers: async (params = {}) => {
    const response = await api.get('/admin/users', { params });
    return response.data;
  },

  // Обновить данные пользователя (например, роль)
  updateUser: async (userId, data) => {
    const response = await api.put(`/users/${userId}`, data);
    return response.data;
  },

  // УПРАВЛЕНИЕ МЕНЮ
  createMenuItem: async (data) => {
    const response = await api.post('/menu/', data);
    return response.data;
  },

  updateMenuItem: async (itemId, data) => {
    const response = await api.put(`/menu/${itemId}`, data);
    return response.data;
  },

  deleteMenuItem: async (itemId) => {
    const response = await api.delete(`/menu/${itemId}`);
    return response.data;
  }
};
