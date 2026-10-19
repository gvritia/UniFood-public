import api from './axios';

export const cartApi = {
  // Получить корзину текущего юзера
  getCart: async () => {
    const response = await api.get('/cart/');
    return response.data;
  },

  // Добавить в корзину
  addToCart: async (menuItemId, quantity = 1) => {
    const response = await api.post('/cart/', {
      menu_item_id: menuItemId,
      quantity: quantity
    });
    return response.data;
  },

  // Обновить количество
  updateQuantity: async (cartItemId, quantity) => {
    const response = await api.patch(`/cart/${cartItemId}`, { quantity });
    return response.data;
  },

  // Удалить позицию
  removeItem: async (cartItemId) => {
    await api.delete(`/cart/${cartItemId}`);
  },

  // Очистить корзину
  clearCart: async () => {
    await api.delete('/cart/');
  }
};