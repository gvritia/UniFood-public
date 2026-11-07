import React, { useState, useEffect, useRef } from 'react';
import { cartApi } from '../api/cart';
import { useAuth } from './auth-context';
import { CartContext } from './cart-context';
import { getApiErrorMessage } from '../api/errors';

export const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState([]);
  const [totalPrice, setTotalPrice] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const requestId = useRef(0);
  const { isAuthenticated, user } = useAuth();

  // Загружаем корзину при авторизации
  useEffect(() => {
    requestId.current += 1;
    if (isAuthenticated) {
      setCartItems([]);
      setTotalPrice(0);
      fetchCart();
    } else {
      setCartItems([]);
      setTotalPrice(0);
      setError('');
      setLoading(false);
    }
  }, [isAuthenticated, user?.id]);

  const fetchCart = async () => {
    const currentRequest = ++requestId.current;
    setLoading(true);
    setError('');
    try {
      const data = await cartApi.getCart();
      if (currentRequest === requestId.current) {
        setCartItems(data.items || []);
        setTotalPrice(data.total_price || 0);
      }
    } catch (error) {
      console.error('Ошибка загрузки корзины:', error);
      if (currentRequest === requestId.current) {
        setError(getApiErrorMessage(error, 'Не удалось загрузить корзину. Попробуйте ещё раз.'));
      }
    } finally {
      if (currentRequest === requestId.current) setLoading(false);
    }
  };

  const addToCart = async (menuItemId, quantity = 1) => {
    try {
      await cartApi.addToCart(menuItemId, quantity);
      await fetchCart();
      return true;
    } catch (error) {
      console.error('Ошибка добавления в корзину:', error);
      throw error;
    }
  };

  const updateQuantity = async (cartItemId, quantity) => {
    try {
      if (quantity <= 0) {
        await cartApi.removeItem(cartItemId);
      } else {
        await cartApi.updateQuantity(cartItemId, quantity);
      }
    } catch (error) {
      console.error('Ошибка обновления количества:', error);
      throw error;
    } finally {
      // Всегда обновляем корзину, чтобы UI соответствовал реальности на сервере
      await fetchCart();
    }
  };

  const removeItem = async (cartItemId) => {
    try {
      await cartApi.removeItem(cartItemId);
      await fetchCart();
    } catch (error) {
      console.error('Ошибка удаления из корзины:', error);
      throw error;
    }
  };

  const clearCart = async () => {
    try {
      await cartApi.clearCart();
      setCartItems([]);
      setTotalPrice(0);
    } catch (error) {
      console.error('Ошибка очистки корзины:', error);
      throw error;
    }
  };

  const value = {
    cartItems,
    totalPrice,
    loading,
    error,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
    refreshCart: fetchCart
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};
