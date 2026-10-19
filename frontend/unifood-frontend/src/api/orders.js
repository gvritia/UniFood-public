import api from './axios';

export const ordersApi = {
  // Создать заказ из корзины (основной флоу)
  createOrder: async () => {
    const response = await api.post('/orders/');
    return response.data;
  },

  // Получить историю своих заказов
  getMyOrders: async () => {
    const response = await api.get('/orders/');
    return response.data;
  }
};