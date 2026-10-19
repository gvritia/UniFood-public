import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Container, Paper, Typography, TextField, Button, Box, Alert,
  Divider, InputAdornment, Card, CardContent, Grid, CircularProgress
} from '@mui/material';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import { useAuth } from '../contexts/AuthContext';
import { profileApi } from '../api/profile';

const ProfilePage = () => {
  const { user, isAuthenticated, refreshUser } = useAuth();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [balanceLoading, setBalanceLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [balanceAmount, setBalanceAmount] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [currentBalance, setCurrentBalance] = useState(0);

  // Задача 3: Автозаполнение суммы при переходе с параметром ?missing=X
  useEffect(() => {
    if (isAuthenticated) {
      loadProfile();
      const missingAmount = searchParams.get('missing');
      if (missingAmount && !isNaN(parseFloat(missingAmount))) {
        setBalanceAmount(parseFloat(missingAmount).toFixed(2));
      }
    }
  }, [isAuthenticated]);

  const loadProfile = async () => {
    try {
      const data = await profileApi.getProfile();
      setFormData({
        name: data.name || '',
        email: data.email || '',
        password: ''
      });
      setCurrentBalance(data.balance || 0);
    } catch (error) {
      console.error('Ошибка загрузки профиля:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const updateData = {
        name: formData.name,
        email: formData.email
      };
      if (formData.password) {
        updateData.password = formData.password;
      }

      await profileApi.updateProfile(updateData);
      setMessage({ type: 'success', text: 'Профиль успешно обновлен!' });
      setFormData({ ...formData, password: '' });
      loadProfile();
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Ошибка обновления профиля' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddBalance = async () => {
    // Задача 14: Округляем до 2 знаков после запятой
    const amount = parseFloat(balanceAmount);
    if (isNaN(amount) || amount <= 0) {
      setMessage({ type: 'error', text: 'Введите корректную сумму' });
      return;
    }

    // Ограничиваем до 2 знаков после запятой
    const roundedAmount = parseFloat(amount.toFixed(2));

    setBalanceLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const result = await profileApi.addBalance(roundedAmount);
      setCurrentBalance(result.balance);
      // Обновляем контекст авторизации
      await refreshUser();
      setMessage({ type: 'success', text: `Баланс пополнен на ${roundedAmount.toFixed(2)} ₽` });
      setBalanceAmount('');
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Ошибка пополнения баланса'
      });
    } finally {
      setBalanceLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Alert severity="info">
          Пожалуйста, войдите, чтобы увидеть свой профиль
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" align="center" gutterBottom fontWeight="bold">
        Профиль пользователя
      </Typography>

      {message.text && (
        <Alert severity={message.type} sx={{ mb: 3 }}>
          {message.text}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Информация о пользователе */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Личная информация
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Имя"
                name="name"
                value={formData.name}
                onChange={handleChange}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PersonIcon />
                    </InputAdornment>
                  )
                }}
              />
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                margin="normal"
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailIcon />
                    </InputAdornment>
                  )
                }}
              />
              <TextField
                fullWidth
                label="Новый пароль (оставьте пустым, чтобы не менять)"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                margin="normal"
                placeholder="••••••••"
              />

              <Button
                type="submit"
                variant="contained"
                fullWidth
                size="large"
                disabled={loading}
                sx={{ mt: 3 }}
              >
                {loading ? 'Сохранение...' : 'Сохранить изменения'}
              </Button>
            </form>
          </Paper>
        </Grid>

        {/* Баланс */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Баланс
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Card variant="outlined" sx={{ mb: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Текущий баланс
                    </Typography>
                    <Typography variant="h3" fontWeight="bold">
                      {currentBalance.toFixed(2)} ₽
                    </Typography>
                  </Box>
                  <AccountBalanceIcon sx={{ fontSize: 64, opacity: 0.3 }} />
                </Box>
              </CardContent>
            </Card>

            <Typography variant="subtitle2" gutterBottom>
              Пополнить баланс:
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <TextField
                fullWidth
                type="number"
                placeholder="Сумма"
                value={balanceAmount}
                onChange={(e) => {
                  const val = e.target.value;
                  // Задача 14: Разрешаем только числа с максимум 2 знаками после запятой
                  if (val === '' || /^\d+(\.\d{0,2})?$/.test(val)) {
                    setBalanceAmount(val);
                  }
                }}
                InputProps={{
                  endAdornment: <InputAdornment position="end">₽</InputAdornment>,
                  inputProps: {
                    step: '0.01',
                    min: '0.01'
                  }
                }}
              />
              <Button
                variant="contained"
                onClick={handleAddBalance}
                disabled={balanceLoading || !balanceAmount}
                sx={{ minWidth: 150 }}
              >
                {balanceLoading ? <CircularProgress size={24} /> : 'Пополнить'}
              </Button>
            </Box>

            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {[100, 500, 1000, 2000].map((amount) => (
                <Button
                  key={amount}
                  variant="outlined"
                  size="small"
                  onClick={() => setBalanceAmount(prev => ((parseFloat(prev) || 0) + amount).toString())}
                >
                  +{amount} ₽
                </Button>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ProfilePage;
