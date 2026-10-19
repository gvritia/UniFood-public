import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Card, CardContent, CardActions,
  Typography, Button, TextField, Chip, Box, CircularProgress,
  Dialog, DialogTitle, DialogContent, IconButton,
  Snackbar, Alert, InputAdornment, Divider
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import CloseIcon from '@mui/icons-material/Close';
import SearchIcon from '@mui/icons-material/Search';
import { menuApi } from '../api/menu';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';

const MenuPage = () => {
  const [allItems, setAllItems] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Все');
  const [selectedDish, setSelectedDish] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [toast, setToast] = useState({ open: false, message: '', severity: 'success' });

  const { addToCart, cartItems, updateQuantity, removeItem } = useCart();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const categories = ['Все', 'Пицца', 'Бургеры', 'Напитки', 'Салаты', 'Десерты', 'Горячее'];

  const getImageUrl = (image_url) => {
    if (!image_url) return 'https://via.placeholder.com/400x300?text=No+Image';
    if (image_url.startsWith('http')) return image_url;
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
    return `${API_URL}${image_url}`;
  };

  useEffect(() => {
    fetchMenu();
  }, []);

  const filterItems = useCallback(() => {
    let filtered = allItems;
    if (selectedCategory !== 'Все') {
      filtered = filtered.filter(item =>
        item.category?.toLowerCase() === selectedCategory.toLowerCase()
      );
    }
    if (search.trim()) {
      const query = search.trim().toLowerCase();
      filtered = filtered.filter(item =>
        item.food_name?.toLowerCase().includes(query) ||
        item.description?.toLowerCase().includes(query) ||
        item.ingredients?.toLowerCase().includes(query) ||
        item.category?.toLowerCase().includes(query)
      );
    }
    setItems(filtered);
  }, [allItems, search, selectedCategory]);

  useEffect(() => {
    filterItems();
  }, [search, selectedCategory, allItems, filterItems]);

  const fetchMenu = async () => {
    setLoading(true);
    try {
      const response = await menuApi.getMenu({});
      setAllItems(response || []);
      setItems(response || []);
    } catch (error) {
      console.error('Ошибка при загрузке меню:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      navigate('/auth/login');
      return;
    }

    try {
      const existingItem = cartItems?.find(ci => ci.menu_item_id === selectedDish.id);
      if (existingItem) {
        await updateQuantity(existingItem.id, quantity);
      } else {
        await addToCart(selectedDish.id, quantity);
      }
      setSelectedDish(null);
      setQuantity(1);
      setToast({ open: true, message: 'Блюдо добавлено в корзину!', severity: 'success' });
    } catch (error) {
      console.error('Ошибка добавления в корзину:', error);
      setToast({ open: true, message: 'Ошибка при добавлении в корзину', severity: 'error' });
    }
  };

  const closeToast = () => setToast(prev => ({ ...prev, open: false }));

  const openDishModal = (dish) => {
    setSelectedDish(dish);
    const existingItem = cartItems?.find(ci => ci.menu_item_id === dish.id);
    setQuantity(existingItem ? existingItem.quantity : 1);
  };

  const closeDishModal = () => {
    setSelectedDish(null);
    setQuantity(1);
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Меню UniFood
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Чтобы просмотреть меню и сделать заказ, пожалуйста, войдите в систему.
        </Typography>
        <Button variant="contained" size="large" onClick={() => navigate('/auth/login')} sx={{ mr: 2 }}>
          Войти
        </Button>
        <Button variant="outlined" size="large" onClick={() => navigate('/auth/register')}>
          Зарегистрироваться
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth={false} sx={{ py: 4, px: { xs: 2, md: 4 } }}>
      <Typography variant="h3" component="h1" align="center" gutterBottom fontWeight="900">
        Меню UniFood
      </Typography>

      <Box sx={{ mb: 6, maxWidth: '800px', mx: 'auto' }}>
        <TextField
          fullWidth
          placeholder="Поиск любимого блюда..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          variant="outlined"
          sx={{ mb: 2, bgcolor: 'background.paper', borderRadius: 2 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="primary" />
              </InputAdornment>
            ),
          }}
        />

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
          {categories.map((cat) => (
            <Chip
              key={cat}
              label={cat}
              onClick={() => setSelectedCategory(cat)}
              color={selectedCategory === cat ? 'primary' : 'default'}
              variant={selectedCategory === cat ? 'filled' : 'outlined'}
              sx={{ fontWeight: 'bold', px: 1 }}
              clickable
            />
          ))}
        </Box>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 12 }}>
          <CircularProgress size={60} thickness={4} />
        </Box>
      ) : items.length === 0 ? (
        <Typography align="center" color="text.secondary" sx={{ py: 12, fontSize: '1.2rem' }}>
          К сожалению, ничего не нашли. Попробуйте другой запрос.
        </Typography>
      ) : (
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              sm: 'repeat(2, 1fr)',
              md: 'repeat(3, 1fr)',
              lg: 'repeat(4, 1fr)',
            },
            gap: 4,
            maxWidth: '1400px',
            mx: 'auto',
          }}
        >
          {items.map((item) => {
            const cartItem = cartItems?.find(ci => ci.menu_item_id === item.id);
            const cartQuantity = cartItem ? cartItem.quantity : 0;

            return (
              <Card
                key={item.id}
                sx={{
                  width: '100%',
                  height: '520px',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 4,
                  overflow: 'hidden',
                  boxShadow: '0 10px 30px rgba(0,0,0,0.08)',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: 'pointer',
                  '&:hover': {
                    transform: 'translateY(-12px)',
                    boxShadow: '0 20px 40px rgba(0,0,0,0.12)'
                  }
                }}
                onClick={() => openDishModal(item)}
              >
                <Box sx={{ height: '260px', flexShrink: 0, position: 'relative', overflow: 'hidden', bgcolor: '#f0f2f5' }}>
                  <img
                    src={getImageUrl(item.image_url)}
                    alt={item.food_name}
                    style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                  />
                  {cartQuantity > 0 && (
                    <Box
                      sx={{
                        position: 'absolute',
                        top: 16,
                        right: 16,
                        bgcolor: 'primary.main',
                        color: 'white',
                        borderRadius: '50%',
                        width: 36,
                        height: 36,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: '900',
                        boxShadow: 3,
                        border: '2px solid white'
                      }}
                    >
                      {cartQuantity}
                    </Box>
                  )}
                </Box>

                <CardContent sx={{ flexGrow: 1, p: 3, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                  <Typography variant="overline" color="primary" sx={{ fontWeight: '900', letterSpacing: '1px', mb: 0.5 }}>
                    {item.category}
                  </Typography>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: '800',
                      lineHeight: '1.4',
                      height: '3.6rem',
                      overflow: 'hidden',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      mb: 1
                    }}
                  >
                    {item.food_name}
                  </Typography>
                  <Box sx={{ mt: 'auto' }}>
                    <Typography variant="body2" color="text.secondary" sx={{ fontWeight: '500' }}>
                      {item.calories ? `${item.calories} ккал` : '\u00A0'}
                    </Typography>
                  </Box>
                </CardContent>

                <Divider sx={{ mx: 3, opacity: 0.5, flexShrink: 0 }} />

                <CardActions sx={{ p: 3, justifyContent: 'space-between', flexShrink: 0 }}>
                  <Typography variant="h5" color="text.primary" sx={{ fontWeight: '900' }}>
                    {item.price} ₽
                  </Typography>

                  {cartQuantity > 0 ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, bgcolor: '#f0f4f8', borderRadius: 3, p: 0.5 }}>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (cartQuantity <= 1) {
                            removeItem(cartItem.id);
                          } else {
                            updateQuantity(cartItem.id, cartQuantity - 1);
                          }
                        }}
                      >
                        <RemoveIcon fontSize="small" />
                      </IconButton>
                      <Typography sx={{ minWidth: 20, textAlign: 'center', fontWeight: '900' }}>
                        {cartQuantity}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          updateQuantity(cartItem.id, cartQuantity + 1);
                        }}
                      >
                        <AddIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  ) : (
                    <Button
                      variant="contained"
                      onClick={(e) => {
                        e.stopPropagation();
                        openDishModal(item);
                      }}
                      sx={{ borderRadius: 3, px: 3, fontWeight: '900', textTransform: 'none' }}
                    >
                      В корзину
                    </Button>
                  )}
                </CardActions>
              </Card>
            );
          })}
        </Box>
      )}

      {selectedDish && (
        <Dialog open={!!selectedDish} onClose={closeDishModal} maxWidth="md" fullWidth>
          <DialogTitle sx={{ m: 0, p: 2.5, fontWeight: '900', fontSize: '1.1rem' }}>
            {selectedDish.food_name}
            <IconButton onClick={closeDishModal} sx={{ position: 'absolute', right: 12, top: 12 }}>
              <CloseIcon />
            </IconButton>
          </DialogTitle>
          <DialogContent dividers sx={{ p: 0 }}>
            <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, minHeight: 280 }}>
              {/* Фото слева */}
              <Box sx={{ width: { xs: '100%', sm: '40%' }, flexShrink: 0, overflow: 'hidden', bgcolor: '#f0f2f5' }}>
                <Box
                  component="img"
                  src={getImageUrl(selectedDish.image_url)}
                  alt={selectedDish.food_name}
                  sx={{ width: '100%', height: '100%', minHeight: { xs: 200, sm: 'auto' }, objectFit: 'cover', display: 'block' }}
                />
              </Box>

              {/* Контент справа */}
              <Box sx={{ flex: 1, p: 3, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Typography variant="overline" color="primary" sx={{ fontWeight: '900', letterSpacing: '1px' }}>
                  {selectedDish.category}
                </Typography>

                {selectedDish.ingredients && (
                  <Typography variant="body2" sx={{ lineHeight: '1.6', color: 'text.secondary' }}>
                    <Box component="span" sx={{ fontWeight: '700', color: 'text.primary' }}>Состав: </Box>
                    {selectedDish.ingredients}
                  </Typography>
                )}

                {selectedDish.calories && (
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: '600' }}>
                    🔥 {selectedDish.calories} ккал
                  </Typography>
                )}

                <Typography variant="h4" color="primary" sx={{ fontWeight: '900', mt: 'auto' }}>
                  {selectedDish.price} ₽
                </Typography>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <Typography variant="body1" sx={{ fontWeight: '700' }}>Кол-во:</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, bgcolor: '#f0f4f8', borderRadius: 3, px: 1.5, py: 0.5 }}>
                    <IconButton onClick={() => setQuantity(q => Math.max(1, q - 1))} size="small">
                      <RemoveIcon fontSize="small" />
                    </IconButton>
                    <Typography variant="h6" sx={{ minWidth: 24, textAlign: 'center', fontWeight: '900' }}>
                      {quantity}
                    </Typography>
                    <IconButton onClick={() => setQuantity(q => q + 1)} size="small">
                      <AddIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </Box>

                <Button
                  onClick={handleAddToCart}
                  variant="contained"
                  size="large"
                  fullWidth
                  sx={{ borderRadius: 3, fontWeight: '900', textTransform: 'none', mt: 1 }}
                >
                  {cartItems?.find(ci => ci.menu_item_id === selectedDish.id)
                    ? `Обновить (${quantity} шт.)`
                    : `В корзину (${quantity} шт.)`}
                </Button>
              </Box>
            </Box>
          </DialogContent>
        </Dialog>
      )}

      <Snackbar open={toast.open} autoHideDuration={3000} onClose={closeToast} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
        <Alert onClose={closeToast} severity={toast.severity} sx={{ width: '100%', borderRadius: 2, fontWeight: 'bold' }}>
          {toast.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default MenuPage;
