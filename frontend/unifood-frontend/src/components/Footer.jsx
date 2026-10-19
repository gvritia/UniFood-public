import React from 'react';
import { Box, Container, Typography, Link, Divider } from '@mui/material';

const Footer = () => {
  return (
    <Box component="footer" sx={{ bgcolor: 'grey.900', color: 'white', py: 4, mt: 'auto' }}>
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', gap: 3 }}>
          {/* О проекте */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              UniFood
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Онлайн-заказ еды в столовой вашего вуза.
              Быстро, удобно и вкусно!
            </Typography>
          </Box>

          {/* Контакты */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              Контакты
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Email: support@unifood.ru
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Телефон: +7 (999) 000-00-00
            </Typography>
          </Box>

          {/* Режим работы */}
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
              Режим работы
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Пн-Пт: 8:00 - 20:00
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              Сб-Вс: 10:00 - 18:00
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ my: 3, borderColor: 'grey.700' }} />

        {/* Копирайт */}
        <Typography variant="body2" align="center" sx={{ opacity: 0.6 }}>
          © {new Date().getFullYear()} UniFood. Все права защищены.
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
