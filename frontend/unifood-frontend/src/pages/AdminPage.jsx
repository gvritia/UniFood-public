import React, { useState, useEffect } from 'react';
import {
  Container, Typography, Box, Paper, Tabs, Tab, Grid, Card, CardContent,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Select, MenuItem, Chip, CircularProgress, Alert, TextField, Button,
  Snackbar, Divider, Dialog, DialogTitle, DialogContent, DialogActions,
  IconButton, InputAdornment
} from '@mui/material';
import AssessmentIcon from '@mui/icons-material/Assessment';
import ShoppingBagIcon from '@mui/icons-material/ShoppingBag';
import PeopleIcon from '@mui/icons-material/People';
import RestaurantMenuIcon from '@mui/icons-material/RestaurantMenu';
import CurrencyRubleIcon from '@mui/icons-material/CurrencyRuble';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import { adminApi } from '../api/admin';
import { menuApi } from '../api/menu';

const STATUS_LABELS = {
  new: { label: 'Новый', color: 'primary' },
  preparing: { label: 'Готовится', color: 'warning' },
  ready: { label: 'Готов', color: 'info' },
  completed: { label: 'Выдан', color: 'success' },
  cancelled: { label: 'Отменен', color: 'error' }
};

const AdminPage = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [orderSearch, setOrderSearch] = useState('');
  const [stats, setStats] = useState(null);
  const [orders, setOrders] = useState([]);
  const [users, setUsers] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [toast, setToast] = useState({ open: false, message: '', severity: 'success' });

  // Состояние для диалога меню
  const [menuDialogOpen, setMenuDialogOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [menuForm, setMenuForm] = useState({
    food_name: '', price: '', category: '', ingredients: '', description: '', image_url: '', calories: ''
  });

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      if (activeTab === 0) {
        const data = await adminApi.getStats();
        setStats(data);
      } else if (activeTab === 1) {
        const data = await adminApi.getOrders(orderSearch ? { search: orderSearch } : {});
        setOrders(data);
      } else if (activeTab === 2) {
        const data = await adminApi.getUsers();
        setUsers(data);
      } else if (activeTab === 3) {
        const data = await menuApi.getMenu();
        setMenuItems(data);
      }
    } catch (error) {
      console.error(error);
      setError('Ошибка при загрузке данных');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await adminApi.updateOrderStatus(orderId, newStatus);
      setOrders(orders.map(o => o.id === orderId ? { ...o, status: newStatus } : o));
      showToast('Статус заказа обновлен');
    } catch (error) {
      const detail = error.response?.data?.detail || 'Ошибка при обновлении статуса';
      showToast(detail, 'error');
    }
  };

  // Задача 4: Поиск заказов в реальном времени (без Enter)
  const handleOrderSearch = (value) => {
    setOrderSearch(value);
  };

  const applyOrderSearch = async () => {
    try {
      setLoading(true);
      const data = await adminApi.getOrders(orderSearch ? { search: orderSearch } : {});
      setOrders(data);
    } catch (error) {
      setError('Ошибка при поиске заказов');
    } finally {
      setLoading(false);
    }
  };

  // Debounce для поиска
  useEffect(() => {
    if (activeTab !== 1) return;
    const timer = setTimeout(() => {
      applyOrderSearch();
    }, 400);
    return () => clearTimeout(timer);
  }, [orderSearch]);

  const handleToggleAdmin = async (userId, currentStatus) => {
    if (!window.confirm(`Вы уверены, что хотите ${currentStatus ? 'снять' : 'назначить'} права администратора?`)) return;
    try {
      await adminApi.updateUser(userId, { is_admin: !currentStatus });
      setUsers(users.map(u => u.id === userId ? { ...u, is_admin: !currentStatus } : u));
      showToast('Роль пользователя обновлена');
    } catch (error) {
      showToast('Ошибка при смене роли', 'error');
    }
  };

  const handleDeleteItem = async (id) => {
    if (!window.confirm('Удалить это блюдо из меню?')) return;
    try {
      await adminApi.deleteMenuItem(id);
      setMenuItems(menuItems.filter(item => item.id !== id));
      showToast('Блюдо удалено');
    } catch (error) {
      showToast('Ошибка при удалении', 'error');
    }
  };

  // Загрузка фото для блюда
  const handleUploadImage = async (id) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/jpeg,image/png,image/webp';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      try {
        const formData = new FormData();
        formData.append('file', file);
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
        const token = localStorage.getItem('token');
        const resp = await fetch(`${API_URL}/menu/${id}/image`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        });
        if (!resp.ok) throw new Error('Ошибка загрузки');
        const data = await resp.json();
        setMenuItems(menuItems.map(m => m.id === id ? data : m));
        showToast('Фото загружено');
      } catch (error) {
        showToast('Ошибка при загрузке фото', 'error');
      }
    };
    input.click();
  };

  const handleOpenMenuDialog = (item = null) => {
    if (item) {
      setEditItem(item);
      setMenuForm({
        food_name: item.food_name,
        price: item.price,
        category: item.category,
        ingredients: item.ingredients || '',
        description: item.description || '',
        image_url: item.image_url || '',
        calories: item.calories || ''
      });
    } else {
      setEditItem(null);
      setMenuForm({
        food_name: '', price: '', category: 'Пицца', ingredients: '', description: '', image_url: '', calories: ''
      });
    }
    setMenuDialogOpen(true);
  };

  const handleMenuSubmit = async () => {
    try {
      const data = { ...menuForm, price: parseFloat(menuForm.price), calories: parseInt(menuForm.calories) || null };
      if (editItem) {
        const updated = await adminApi.updateMenuItem(editItem.id, data);
        setMenuItems(menuItems.map(m => m.id === editItem.id ? updated : m));
        showToast('Блюдо обновлено');
      } else {
        const created = await adminApi.createMenuItem(data);
        setMenuItems([...menuItems, created]);
        showToast('Блюдо добавлено');
      }
      setMenuDialogOpen(false);
    } catch (error) {
      showToast('Ошибка при сохранении', 'error');
    }
  };

  const showToast = (message, severity = 'success') => setToast({ open: true, message, severity });
  const closeToast = () => setToast(prev => ({ ...prev, open: false }));
  const handleTabChange = (event, newValue) => setActiveTab(newValue);

  if (loading && !stats && activeTab === 0) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 5 }}><CircularProgress /></Box>;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>Панель Администратора</Typography>
          <Typography variant="body1" color="text.secondary">Управление платформой UniFood</Typography>
        </Box>
        {activeTab === 3 && (
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenMenuDialog()}>
            Добавить блюдо
          </Button>
        )}
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Paper elevation={0} sx={{ borderRadius: 3, overflow: 'hidden', border: '1px solid #e0e0e0' }}>
        <Tabs value={activeTab} onChange={handleTabChange} variant="scrollable" scrollButtons="auto" sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: '#f8f9fa' }}>
          <Tab icon={<AssessmentIcon />} label="Статистика" iconPosition="start" />
          <Tab icon={<ShoppingBagIcon />} label="Заказы" iconPosition="start" />
          <Tab icon={<PeopleIcon />} label="Пользователи" iconPosition="start" />
          <Tab icon={<RestaurantMenuIcon />} label="Меню" iconPosition="start" />
        </Tabs>

        <Box sx={{ p: { xs: 2, sm: 4 }, minHeight: 400 }}>
          {activeTab === 0 && stats && (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={0} sx={{ bgcolor: '#e3f2fd', borderRadius: 2 }}><CardContent>
                  <Typography color="text.secondary" variant="subtitle2">Выручка (День)</Typography>
                  <Typography variant="h4" fontWeight="bold">{stats.today_revenue} ₽</Typography>
                </CardContent></Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={0} sx={{ bgcolor: '#e8f5e9', borderRadius: 2 }}><CardContent>
                  <Typography color="text.secondary" variant="subtitle2">Всего выручка</Typography>
                  <Typography variant="h4" fontWeight="bold">{stats.total_revenue} ₽</Typography>
                </CardContent></Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={0} sx={{ bgcolor: '#fff3e0', borderRadius: 2 }}><CardContent>
                  <Typography color="text.secondary" variant="subtitle2">Заказов</Typography>
                  <Typography variant="h4" fontWeight="bold">{stats.total_orders}</Typography>
                </CardContent></Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={0} sx={{ bgcolor: '#f3e5f5', borderRadius: 2 }}><CardContent>
                  <Typography color="text.secondary" variant="subtitle2">Юзеров</Typography>
                  <Typography variant="h4" fontWeight="bold">{stats.total_users}</Typography>
                </CardContent></Card>
              </Grid>
            </Grid>
          )}

          {activeTab === 1 && (
            <>
              {/* Задача 4: Поиск заказов */}
              <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                <TextField
                  fullWidth
                  placeholder="Поиск по номеру заказа..."
                  value={orderSearch}
                  onChange={(e) => handleOrderSearch(e.target.value)}
                  variant="outlined"
                  size="small"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
              <TableContainer sx={{ overflowX: 'auto' }}>
                <Table sx={{ minWidth: 700 }}>
                  <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                    <TableRow>
                      <TableCell fontWeight="bold">Номер</TableCell>
                      <TableCell fontWeight="bold">Клиент</TableCell>
                      <TableCell fontWeight="bold">Сумма</TableCell>
                      <TableCell fontWeight="bold">Статус</TableCell>
                      <TableCell fontWeight="bold">Действие</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {orders.map((order) => (
                      <TableRow key={order.id} hover>
                        <TableCell fontWeight="bold">{order.order_number}</TableCell>
                        <TableCell>{order.user?.email || 'Гость'}</TableCell>
                        <TableCell>{order.total_price.toFixed(2)} ₽</TableCell>
                        <TableCell>
                          <Chip label={STATUS_LABELS[order.status]?.label || order.status} color={STATUS_LABELS[order.status]?.color || 'default'} size="small" />
                        </TableCell>
                        <TableCell>
                          {/* Задача 7: Кнопки статусов вместо Select */}
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {order.status === 'completed' || order.status === 'cancelled' ? (
                              // Задача 11: Нельзя менять статус "Выдан" и "Отменён"
                              <Chip
                                label={order.status === 'completed' ? 'Выдан' : 'Отменён'}
                                color={order.status === 'completed' ? 'success' : 'error'}
                                size="small"
                              />
                            ) : (
                              Object.keys(STATUS_LABELS).map((key) => (
                                <Chip
                                  key={key}
                                  label={STATUS_LABELS[key].label}
                                  color={STATUS_LABELS[key].color}
                                  variant={order.status === key ? 'filled' : 'outlined'}
                                  size="small"
                                  onClick={() => handleStatusChange(order.id, key)}
                                  clickable
                                  sx={{ cursor: 'pointer', fontSize: '0.75rem' }}
                                />
                              ))
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </>
          )}

          {activeTab === 2 && (
            <TableContainer sx={{ overflowX: 'auto' }}>
              <Table sx={{ minWidth: 600 }}>
                <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                  <TableRow>
                    <TableCell fontWeight="bold">Имя</TableCell>
                    <TableCell fontWeight="bold">Email</TableCell>
                    <TableCell fontWeight="bold">Роль</TableCell>
                    <TableCell fontWeight="bold">Баланс</TableCell>
                    <TableCell align="right" fontWeight="bold">Действие</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users.map((u) => (
                    <TableRow key={u.id} hover>
                      <TableCell>{u.name}</TableCell>
                      <TableCell>{u.email}</TableCell>
                      <TableCell>{u.is_admin ? <Chip label="Админ" color="secondary" size="small" /> : <Chip label="Юзер" size="small" />}</TableCell>
                      <TableCell fontWeight="bold">{u.balance.toFixed(2)} ₽</TableCell>
                      <TableCell align="right">
                        <Button size="small" onClick={() => handleToggleAdmin(u.id, u.is_admin)} variant="outlined" color={u.is_admin ? "error" : "primary"}>
                          {u.is_admin ? "Снять права" : "Сделать админом"}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {activeTab === 3 && (
            <TableContainer sx={{ overflowX: 'auto' }}>
              <Table sx={{ minWidth: 600 }}>
                <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                  <TableRow>
                    <TableCell fontWeight="bold">Название</TableCell>
                    <TableCell fontWeight="bold">Категория</TableCell>
                    <TableCell fontWeight="bold">Цена</TableCell>
                    <TableCell align="right" fontWeight="bold">Действия</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {menuItems.map((item) => (
                    <TableRow key={item.id} hover>
                      <TableCell fontWeight="bold">{item.food_name}</TableCell>
                      <TableCell><Chip label={item.category} size="small" variant="outlined" /></TableCell>
                      <TableCell>{item.price} ₽</TableCell>
                      <TableCell align="right">
                        <IconButton size="small" onClick={() => handleUploadImage(item.id)} color="info" title="Загрузить фото">
                          <PhotoCameraIcon />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleOpenMenuDialog(item)} color="primary">
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleDeleteItem(item.id)} color="error">
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      </Paper>

      {/* Диалог добавления/редактирования меню */}
      <Dialog open={menuDialogOpen} onClose={() => setMenuDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editItem ? 'Редактировать блюдо' : 'Добавить новое блюдо'}</DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField fullWidth label="Название блюда" value={menuForm.food_name} onChange={(e) => setMenuForm({...menuForm, food_name: e.target.value})} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Цена (₽)" type="number" value={menuForm.price} onChange={(e) => setMenuForm({...menuForm, price: e.target.value})} />
            </Grid>
            <Grid item xs={6}>
              <Select fullWidth value={menuForm.category} onChange={(e) => setMenuForm({...menuForm, category: e.target.value})}>
                <MenuItem value="Пицца">Пицца</MenuItem>
                <MenuItem value="Бургеры">Бургеры</MenuItem>
                <MenuItem value="Напитки">Напитки</MenuItem>
                <MenuItem value="Салаты">Салаты</MenuItem>
                <MenuItem value="Десерты">Десерты</MenuItem>
                <MenuItem value="Горячее">Горячее</MenuItem>
              </Select>
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Калории" type="number" value={menuForm.calories} onChange={(e) => setMenuForm({...menuForm, calories: e.target.value})} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="URL изображения" value={menuForm.image_url} onChange={(e) => setMenuForm({...menuForm, image_url: e.target.value})} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={2} label="Состав" value={menuForm.ingredients} onChange={(e) => setMenuForm({...menuForm, ingredients: e.target.value})} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={3} label="Описание" value={menuForm.description} onChange={(e) => setMenuForm({...menuForm, description: e.target.value})} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMenuDialogOpen(false)}>Отмена</Button>
          <Button onClick={handleMenuSubmit} color="primary" variant="contained">Сохранить</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={toast.open} autoHideDuration={4000} onClose={closeToast} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        <Alert onClose={closeToast} severity={toast.severity} variant="filled" sx={{ width: '100%' }}>{toast.message}</Alert>
      </Snackbar>
    </Container>
  );
};

export default AdminPage;
