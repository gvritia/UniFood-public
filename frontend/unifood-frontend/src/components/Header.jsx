import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Button, Box, IconButton, Badge,
  Avatar, Menu, MenuItem, Chip, Drawer, List, ListItem, ListItemText,
  ListItemIcon, Divider, Container
} from '@mui/material';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import MenuIcon from '@mui/icons-material/Menu';
import RestaurantMenuIcon from '@mui/icons-material/RestaurantMenu';
import HistoryIcon from '@mui/icons-material/History';
import LogoutIcon from '@mui/icons-material/Logout';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import PersonIcon from '@mui/icons-material/Person';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';

const Header = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const { cartItems } = useCart();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const cartItemsCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  const handleMenuOpen = (event) => setAnchorEl(event.currentTarget);
  const handleMenuClose = () => setAnchorEl(null);
  const handleDrawerToggle = () => setMobileOpen(!mobileOpen);

  const handleLogout = () => {
    logout();
    handleMenuClose();
    setMobileOpen(false);
  };

  const isActive = (path) => location.pathname === path;

  const navLinks = [
    { title: 'Меню', path: '/menu', icon: <RestaurantMenuIcon /> },
    { title: 'Заказы', path: '/orders', icon: <HistoryIcon />, auth: true },
  ];

  return (
    <>
      <AppBar position="sticky" color="primary" elevation={1} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Container maxWidth="lg">
          <Toolbar disableGutters>
            {/* Бургер для мобилок */}
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>

            {/* Логотип */}
            <Typography
              variant="h6"
              component={Link}
              to="/"
              sx={{
                textDecoration: 'none',
                color: 'inherit',
                fontWeight: 'bold',
                mr: { xs: 0, sm: 4 },
                flexGrow: { xs: 1, sm: 0 },
                textAlign: { xs: 'center', sm: 'left' }
              }}
            >
              UniFood
            </Typography>

            {/* Навигация (Desktop) */}
            <Box sx={{ flexGrow: 1, display: { xs: 'none', sm: 'flex' }, gap: 1 }}>
              <Button
                color="inherit"
                component={Link}
                to="/menu"
                sx={{ fontWeight: isActive('/menu') ? 'bold' : 'normal' }}
              >
                Меню
              </Button>
              {isAuthenticated && (
                <>
                  <Button
                    color="inherit"
                    component={Link}
                    to="/cart"
                    sx={{ fontWeight: isActive('/cart') ? 'bold' : 'normal' }}
                  >
                    <Badge badgeContent={cartItemsCount} color="error">
                      <ShoppingCartIcon />
                    </Badge>
                  </Button>
                  <Button
                    color="inherit"
                    component={Link}
                    to="/orders"
                    sx={{ fontWeight: isActive('/orders') ? 'bold' : 'normal' }}
                  >
                    Заказы
                  </Button>
                </>
              )}
            </Box>

            {/* Профиль / Баланс */}
            {isAuthenticated ? (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Chip
                  icon={<AccountBalanceIcon />}
                  label={`${user?.balance?.toFixed(2) || '0.00'} ₽`}
                  sx={{ 
                    mr: { xs: 0, sm: 2 }, 
                    bgcolor: 'rgba(255,255,255,0.2)',
                    color: 'white',
                    fontWeight: 'bold'
                  }}
                />
                
                <Box sx={{ display: { xs: 'none', sm: 'block' }, mr: 2 }}>
                  <Typography variant="body2">{user?.name}</Typography>
                </Box>

                <IconButton onClick={handleMenuOpen} size="small">
                  <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                    {user?.name?.charAt(0)}
                  </Avatar>
                </IconButton>
                
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                  sx={{ display: { xs: 'none', sm: 'block' } }}
                >
                  <MenuItem component={Link} to="/profile" onClick={handleMenuClose}>Профиль</MenuItem>
                  {user?.is_admin && (
                    <MenuItem component={Link} to="/admin" onClick={handleMenuClose} sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                      Админ Панель
                    </MenuItem>
                  )}
                  <MenuItem onClick={handleLogout}>Выйти</MenuItem>
                </Menu>
              </Box>
            ) : (
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button color="inherit" component={Link} to="/auth/login" sx={{ display: { xs: 'none', sm: 'flex' } }}>
                  Войти
                </Button>
                <Button color="secondary" variant="contained" component={Link} to="/auth/register">
                  Присоединиться
                </Button>
              </Box>
            )}
          </Toolbar>
        </Container>
      </AppBar>

      {/* Мобильный Drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 250 },
        }}
      >
        <Box sx={{ width: 250 }} onClick={handleDrawerToggle}>
          <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
            <Typography variant="h6" fontWeight="bold">UniFood</Typography>
            {isAuthenticated && (
              <Typography variant="body2" sx={{ opacity: 0.8 }}>{user?.name}</Typography>
            )}
          </Box>
          <List>
            {navLinks.map((link) => (
              (!link.auth || isAuthenticated) && (
                <ListItem button key={link.title} component={Link} to={link.path}>
                  <ListItemIcon>{link.icon}</ListItemIcon>
                  <ListItemText primary={link.title} />
                </ListItem>
              )
            ))}
            {!isAuthenticated && (
              <>
                <Divider />
                <ListItem button component={Link} to="/auth/login">
                  <ListItemIcon><AccountCircleIcon /></ListItemIcon>
                  <ListItemText primary="Войти" />
                </ListItem>
                <ListItem button component={Link} to="/auth/register">
                  <ListItemIcon><RestaurantMenuIcon /></ListItemIcon>
                  <ListItemText primary="Регистрация" />
                </ListItem>
              </>
            )}
            {isAuthenticated && (
              <>
                <ListItem button component={Link} to="/cart">
                  <ListItemIcon>
                    <Badge badgeContent={cartItemsCount} color="error">
                      <ShoppingCartIcon />
                    </Badge>
                  </ListItemIcon>
                  <ListItemText primary="Корзина" />
                </ListItem>
                <ListItem button component={Link} to="/profile">
                  <ListItemIcon><PersonIcon /></ListItemIcon>
                  <ListItemText primary="Профиль" />
                </ListItem>
                {user?.is_admin && (
                  <ListItem button component={Link} to="/admin">
                    <ListItemIcon><AdminPanelSettingsIcon color="primary" /></ListItemIcon>
                    <ListItemText primary="Админ Панель" sx={{ color: 'primary.main', fontWeight: 'bold' }} />
                  </ListItem>
                )}
                <Divider />
                <ListItem button onClick={handleLogout}>
                  <ListItemIcon><LogoutIcon /></ListItemIcon>
                  <ListItemText primary="Выйти" />
                </ListItem>
              </>
            )}
          </List>
        </Box>
      </Drawer>
    </>
  );
};

export default Header;
