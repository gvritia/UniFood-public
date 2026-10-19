import React, { createContext, useState, useContext, useEffect } from 'react';
import { cartApi } from '../api/cart';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState([]);
  const [totalPrice, setTotalPrice] = useState(0);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  // Загружаем корзину при авторизации
  useEffect(() => {
    if (isAuthenticated) {
      fetchCart();
    } else {
      setCartItems([]);
      setTotalPrice(0);
    }
  }, [isAuthenticated]);

  const fetchCart = async () => {
    setLoading(true);
    try {
      const data = await cartApi.getCart();
      setCartItems(data.items || []);
      setTotalPrice(data.total_price || 0);
    } catch (error) {
      console.error('Ошибка загрузки корзины:', error);
      setCartItems([]);
      setTotalPrice(0);
    } finally {
      setLoading(false);
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
