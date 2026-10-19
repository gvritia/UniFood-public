import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Container, Typography, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Button, Box, IconButton,
  Divider, Alert, Chip, Card, CardContent, TextField,
  Dialog, DialogTitle, DialogContent, DialogActions, Snackbar
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import DeleteIcon from '@mui/icons-material/Delete';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import { ordersApi } from '../api/orders';

const CartPage = () => {
  const { cartItems, totalPrice, loading, updateQuantity, removeItem, clearCart, refreshCart } = useCart();
  const { isAuthenticated, user, refreshUser } = useAuth();
  const navigate = useNavigate();
  // Задача 15: Локальное состояние для ручного ввода количества
  const [quantities, setQuantities] = useState({});
  // Задача 2: Состояние для диалога оплаты
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [checkoutError, setCheckoutError] = useState(null);

  const handleQuantityChange = (itemId, value) => {
    // Разрешаем только числа
    const num = parseInt(value, 10);
    if (isNaN(num) || num < 0) {
      setQuantities(prev => ({ ...prev, [itemId]: value === '' ? '' : 0 }));
    } else {
      setQuantities(prev => ({ ...prev, [itemId]: num }));
    }
  };

  const handleQuantitySubmit = (itemId) => {
    const qty = quantities[itemId];
    if (qty === undefined || qty === '') return;
    const num = parseInt(qty, 10);
    if (isNaN(num) || num <= 0) {
      removeItem(itemId);
    } else {
      updateQuantity(itemId, num);
    }
  };

  const handleQuantityBlur = (itemId) => {
    handleQuantitySubmit(itemId);
  };

  const incrementQuantity = (itemId, currentQty) => {
    setQuantities(prev => ({ ...prev, [itemId]: currentQty + 1 }));
    updateQuantity(itemId, currentQty + 1);
  };

  const decrementQuantity = (itemId, currentQty) => {
    if (currentQty <= 1) {
      removeItem(itemId);
    } else {
      setQuantities(prev => ({ ...prev, [itemId]: currentQty - 1 }));
      updateQuantity(itemId, currentQty - 1);
    }
  };

  const handleCheckout = async () => {
    if (!isAuthenticated) {
      navigate('/auth/login');
      return;
    }

    // Задача 2+3: Проверяем баланс — открываем диалог вместо alert
    // Округляем до 2 знаков, чтобы избежать проблем с float
    const balance = parseFloat((user.balance || 0).toFixed(2));
    const total = parseFloat(totalPrice.toFixed(2));
    if (balance < total) {
      const missing = (total - balance).toFixed(2);
      setCheckoutError(`Недостаточно средств. Не хватает: ${missing} ₽`);
      setPaymentDialogOpen(true);
      return;
    }

    try {
      await ordersApi.createOrder();
      // Очищаем корзину после успешного заказа
      await clearCart();
      // Обновляем данные пользователя после заказа
      await refreshUser();
      navigate('/orders', { state: { message: 'Заказ успешно оформлен!' } });
    } catch (error) {
      console.error('Ошибка оформления заказа:', error);
      const errorMessage = error.response?.data?.detail || 'Ошибка при оформлении заказа. Попробуйте позже.';
      setCheckoutError(errorMessage);
      setPaymentDialogOpen(true);
    }
  };

  const handleGoToProfile = () => {
    // Задача 3: Передаём недостающую сумму в URL
    const balance = parseFloat((user.balance || 0).toFixed(2));
    const total = parseFloat(totalPrice.toFixed(2));
    if (balance < total) {
      const missing = (total - balance).toFixed(2);
      navigate(`/profile?missing=${missing}`);
    } else {
      navigate('/profile');
    }
    setPaymentDialogOpen(false);
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Alert severity="info" sx={{ mb: 3 }}>
          Пожалуйста, <Link to="/auth/login">войдите</Link>, чтобы увидеть свою корзину
        </Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
        <Typography>Загрузка корзины...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" align="center" gutterBottom fontWeight="bold">
        Корзина
      </Typography>

      {/* Отображение баланса */}
      {isAuthenticated && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AccountBalanceIcon />
              <Typography variant="body1">Ваш баланс:</Typography>
            </Box>
            <Chip
              label={`${user?.balance?.toFixed(2) || '0.00'} ₽`}
              sx={{ 
                bgcolor: 'rgba(255,255,255,0.3)', 
                color: 'white',
                fontWeight: 'bold',
                fontSize: '1.1rem'
              }}
            />
          </Box>
        </Paper>
      )}

      {cartItems.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Ваша корзина пуста
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 3 }}>
            Добавьте блюда из меню, чтобы сделать заказ
          </Typography>
          <Button 
            variant="contained" 
            component={Link} 
            to="/menu"
            size="large"
          >
            Перейти в меню
          </Button>
        </Paper>
      ) : (
        <>
          {/* Вид для десктопа (Таблица) */}
          <TableContainer component={Paper} sx={{ mt: 4, display: { xs: 'none', sm: 'block' } }}>
            <Table>
              <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell>Блюдо</TableCell>
                  <TableCell align="right">Цена</TableCell>
                  <TableCell align="center">Количество</TableCell>
                  <TableCell align="right">Сумма</TableCell>
                  <TableCell align="center">Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {cartItems.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <Typography fontWeight="bold">{item.menu_item?.food_name || 'Блюдо удалено'}</Typography>
                      {item.menu_item?.category && (
                        <Typography variant="caption" color="text.secondary">
                          {item.menu_item.category}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell align="right">{item.menu_item?.price || 0} ₽</TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <IconButton size="small" onClick={() => decrementQuantity(item.id, item.quantity)}>
                          <RemoveIcon />
                        </IconButton>
                        <TextField
                          size="small"
                          type="text"
                          value={quantities[item.id] ?? item.quantity}
                          onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                          onBlur={() => handleQuantityBlur(item.id)}
                          onKeyDown={(e) => { if (e.key === 'Enter') handleQuantitySubmit(item.id); }}
                          inputProps={{
                            style: { textAlign: 'center', minWidth: 40 },
                            inputMode: 'numeric',
                            pattern: '[0-9]*'
                          }}
                          sx={{ mx: 1, width: 70 }}
                        />
                        <IconButton size="small" onClick={() => incrementQuantity(item.id, item.quantity)}>
                          <AddIcon />
                        </IconButton>
                      </Box>
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                      {(item.menu_item?.price * item.quantity || 0).toFixed(2)} ₽
                    </TableCell>
                    <TableCell align="center">
                      <IconButton color="error" onClick={() => removeItem(item.id)}>
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Вид для мобилок (Карточки) */}
          <Box sx={{ display: { xs: 'block', sm: 'none' }, mt: 2 }}>
            {cartItems.map((item) => (
              <Card key={item.id} sx={{ mb: 2, border: '1px solid #eee' }} elevation={0}>
                <CardContent sx={{ pb: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {item.menu_item?.food_name || 'Блюдо удалено'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {item.menu_item?.price} ₽ / шт.
                      </Typography>
                    </Box>
                    <IconButton color="error" size="small" onClick={() => removeItem(item.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', bgcolor: '#f5f5f5', borderRadius: 1 }}>
                      <IconButton size="small" onClick={() => decrementQuantity(item.id, item.quantity)}>
                        <RemoveIcon fontSize="small" />
                      </IconButton>
                      <TextField
                        size="small"
                        type="text"
                        value={quantities[item.id] ?? item.quantity}
                        onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                        onBlur={() => handleQuantityBlur(item.id)}
                        onKeyDown={(e) => { if (e.key === 'Enter') handleQuantitySubmit(item.id); }}
                        inputProps={{
                          style: { textAlign: 'center', minWidth: 30, padding: '4px' },
                          inputMode: 'numeric',
                          pattern: '[0-9]*'
                        }}
                        sx={{ mx: 0.5, width: 60 }}
                      />
                      <IconButton size="small" onClick={() => incrementQuantity(item.id, item.quantity)}>
                        <AddIcon fontSize="small" />
                      </IconButton>
                    </Box>
                    <Typography variant="subtitle1" fontWeight="bold" color="primary">
                      {(item.menu_item?.price * item.quantity || 0).toFixed(2)} ₽
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>

          <Paper sx={{ p: 3, mt: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Итого:</Typography>
              <Typography variant="h5" color="primary" fontWeight="bold">
                {totalPrice.toFixed(2)} ₽
              </Typography>
            </Box>
            <Divider sx={{ my: 2 }} />
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button 
                variant="outlined" 
                color="error"
                onClick={clearCart}
              >
                Очистить корзину
              </Button>
              <Button 
                variant="contained" 
                size="large"
                onClick={handleCheckout}
                disabled={totalPrice === 0}
              >
                Оформить заказ
              </Button>
            </Box>
          </Paper>
        </>
      )}

      {/* Задача 2: Диалог при ошибке оплаты */}
      <Dialog open={paymentDialogOpen} onClose={() => setPaymentDialogOpen(false)}>
        <DialogTitle color="error">Ошибка оплаты</DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            {checkoutError}
          </Alert>
          {(() => {
            const balance = parseFloat((user.balance || 0).toFixed(2));
            const total = parseFloat(totalPrice.toFixed(2));
            return balance < total ? (
              <Typography variant="body2" color="text.secondary">
                Ваш баланс: {balance.toFixed(2)} ₽<br />
                Сумма заказа: {total.toFixed(2)} ₽<br />
                Не хватает: {(total - balance).toFixed(2)} ₽
              </Typography>
            ) : null;
          })()}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPaymentDialogOpen(false)}>Закрыть</Button>
          {(() => {
            const balance = parseFloat((user.balance || 0).toFixed(2));
            const total = parseFloat(totalPrice.toFixed(2));
            return balance < total ? (
              <Button
                onClick={handleGoToProfile}
                variant="contained"
                color="primary"
              >
                Пополнить баланс
              </Button>
            ) : null;
          })()}
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CartPage;
