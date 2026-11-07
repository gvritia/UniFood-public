import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Container, Box, Typography, TextField, Button, Paper, Alert, Link as MuiLink
} from '@mui/material';
import { useAuth } from '../contexts/auth-context';
import { getApiErrorMessage } from '../api/errors';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await login(email, password);
      // Админ — сразу на админ-панель, обычный пользователь — в меню
      if (data.user?.is_admin) {
        navigate('/admin');
      } else {
        navigate('/menu');
      }
    } catch (err) {
      setError(getApiErrorMessage(err, 'Ошибка входа. Проверьте email и пароль.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" align="center" gutterBottom fontWeight="bold">
            Вход
          </Typography>
          <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 3 }}>
            Войдите, чтобы продолжить заказ
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          {location.state?.profileUpdated && (
            <Alert severity="success" sx={{ mb: 3 }}>Email изменён. Войдите с новым адресом.</Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
              required
              autoComplete="email"
              autoFocus
            />
            <TextField
              fullWidth
              label="Пароль"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
              autoComplete="current-password"
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, mb: 2 }}
            >
              {loading ? 'Вход...' : 'Войти'}
            </Button>

            <Typography align="center" variant="body2">
              Нет аккаунта?{' '}
              <MuiLink component={Link} to="/auth/register" underline="hover">
                Зарегистрироваться
              </MuiLink>
            </Typography>
          </form>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;
