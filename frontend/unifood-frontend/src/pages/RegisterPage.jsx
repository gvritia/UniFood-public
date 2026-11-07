import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Container, Box, Typography, TextField, Button, Paper, Alert, Link as MuiLink
} from '@mui/material';
import { useAuth } from '../contexts/auth-context';
import { getApiErrorMessage } from '../api/errors';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    if (formData.password.length < 8 ||
        !/[A-ZА-ЯЁ]/.test(formData.password) ||
        !/[a-zа-яё]/.test(formData.password) ||
        !/\d/.test(formData.password) ||
        ![...formData.password].some((char) => "!@#$%^&*()_+-=[]{};':\"\\|,.<>/?".includes(char))) {
      setError('Пароль: минимум 8 символов, заглавная и строчная буква, цифра и спецсимвол.');
      return;
    }

    setLoading(true);

    try {
      await register({
        name: formData.name,
        email: formData.email,
        password: formData.password
      });
      // После регистрации автоматически входим
      navigate('/auth/login', { state: { registered: true } });
    } catch (err) {
      setError(getApiErrorMessage(err, 'Ошибка регистрации. Возможно, email уже занят.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" align="center" gutterBottom fontWeight="bold">
            Регистрация
          </Typography>
          <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 3 }}>
            Создайте аккаунт для заказа еды
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Пароль: минимум 8 символов, заглавная и строчная буква, цифра и спецсимвол.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Имя"
              name="name"
              value={formData.name}
              onChange={handleChange}
              margin="normal"
              required
              autoComplete="name"
              autoFocus
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
              autoComplete="email"
            />
            <TextField
              fullWidth
              label="Пароль"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              required
              autoComplete="new-password"
            />
            <TextField
              fullWidth
              label="Подтвердите пароль"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              margin="normal"
              required
              autoComplete="new-password"
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, mb: 2 }}
            >
              {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </Button>

            <Typography align="center" variant="body2">
              Уже есть аккаунт?{' '}
              <MuiLink component={Link} to="/auth/login" underline="hover">
                Войти
              </MuiLink>
            </Typography>
          </form>
        </Paper>
      </Box>
    </Container>
  );
};

export default RegisterPage;
