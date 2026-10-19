import React from 'react';
import { Link } from 'react-router-dom';
import { Box, Typography, Button, Container } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

// ─── Design Tokens ─────────────────────────────────────────────────────────
const NAVY    = '#0D1B2A';
const BLUE    = '#1B4F8A';
const ACCENT  = '#4A90D9';
const LIGHT   = '#EEF4FF';
const WHITE   = '#FFFFFF';

// ─── Images ────────────────────────────────────────────────────────────────
const HERO_IMG    = 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1920&q=80';
const FEATURE_IMG = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=900&q=80';
const STEP1_IMG   = 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=600&q=80';
const STEP2_IMG   = 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?auto=format&fit=crop&w=600&q=80';
const STEP3_IMG   = 'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=600&q=80';

const HomePage = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Box sx={{ bgcolor: LIGHT, fontFamily: "'Inter', sans-serif", overflow: 'hidden' }}>

      {/* ── HERO ────────────────────────────────────────────── */}
      <Box sx={{ position: 'relative', height: { xs: '65vh', md: '85vh' }, overflow: 'hidden' }}>
        <Box
          component="img"
          src={HERO_IMG}
          alt="UniFood hero"
          sx={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'center 60%' }}
        />
        <Box
          sx={{
            position: 'absolute',
            inset: 0,
            background: `linear-gradient(to bottom, rgba(13,27,42,0.35) 0%, rgba(13,27,42,0.85) 100%)`,
          }}
        />
        {/* Logo */}
        <Typography
          sx={{
            position: 'absolute',
            top: 28,
            left: 36,
            fontFamily: "'Bebas Neue', sans-serif",
            fontSize: { xs: '1.8rem', md: '2.4rem' },
            color: WHITE,
            letterSpacing: 4,
          }}
        >
          UNIFOOD
        </Typography>
        {/* Hero Content */}
        <Box
          sx={{
            position: 'absolute',
            bottom: { xs: 36, md: 64 },
            left: { xs: 24, md: 60 },
            right: { xs: 24, md: '32%' },
          }}
        >
          <Typography
            component="h1"
            sx={{
              fontFamily: "'Bebas Neue', sans-serif",
              fontSize: { xs: '3.2rem', sm: '5rem', md: '7rem' },
              color: WHITE,
              lineHeight: 1,
              letterSpacing: 2,
              mb: 3,
            }}
          >
            ЕШЬ ВКУСНО.<br />
            <Box component="span" sx={{ color: ACCENT }}>ЖИВ</Box>И ЯРКО.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              component={Link}
              to="/menu"
              variant="contained"
              sx={{
                bgcolor: ACCENT,
                color: WHITE,
                fontFamily: "'Bebas Neue', sans-serif",
                fontSize: '1.1rem',
                letterSpacing: 2,
                px: 5,
                py: 1.5,
                borderRadius: '6px',
                boxShadow: 'none',
                '&:hover': { bgcolor: BLUE },
              }}
            >
              В МЕНЮ
            </Button>
            {!isAuthenticated && (
              <Button
                component={Link}
                to="/auth/login"
                sx={{
                  color: WHITE,
                  border: `2px solid ${WHITE}`,
                  fontFamily: "'Bebas Neue', sans-serif",
                  fontSize: '1.1rem',
                  letterSpacing: 2,
                  px: 5,
                  py: 1.5,
                  borderRadius: '6px',
                  '&:hover': { bgcolor: 'rgba(255,255,255,0.12)' },
                }}
              >
                ВОЙТИ
              </Button>
            )}
          </Box>
        </Box>
      </Box>

      {/* ── FEATURE SECTION ─────────────────────────────────── */}
      <Box sx={{ bgcolor: WHITE, py: { xs: 8, md: 14 } }}>
        <Container maxWidth="lg">
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', md: 'row' },
              alignItems: 'center',
              gap: { xs: 6, md: 12 },
            }}
          >
            {/* Text */}
            <Box sx={{ flex: 1 }}>
              <Typography
                sx={{
                  fontFamily: "'Bebas Neue', sans-serif",
                  fontSize: { xs: '2.4rem', md: '3.5rem' },
                  color: NAVY,
                  lineHeight: 1.05,
                  mb: 3,
                  letterSpacing: 1,
                }}
              >
                СТУДЕНЧЕСКИЙ ОБЕД<br />
                <Box component="span" sx={{ color: ACCENT }}>НОВОГО УРОВНЯ</Box>
              </Typography>
              <Typography
                sx={{
                  fontSize: '1rem',
                  color: NAVY,
                  opacity: 0.7,
                  lineHeight: 1.9,
                  mb: 4,
                  maxWidth: 420,
                }}
              >
                UniFood — современный сервис заказа еды в столовых вашего университета.
                Просматривайте меню, оформляйте заказ онлайн и забирайте
                без очередей по номеру заказа.
              </Typography>
              <Button
                component={Link}
                to={isAuthenticated ? '/menu' : '/auth/register'}
                variant="contained"
                sx={{
                  bgcolor: BLUE,
                  color: WHITE,
                  fontFamily: "'Bebas Neue', sans-serif",
                  fontSize: '1.1rem',
                  letterSpacing: 2,
                  px: 5,
                  py: 1.5,
                  borderRadius: '6px',
                  boxShadow: 'none',
                  '&:hover': { bgcolor: NAVY },
                }}
              >
                {isAuthenticated ? 'ОТКРЫТЬ МЕНЮ' : 'НАЧАТЬ СЕЙЧАС'}
              </Button>
            </Box>

            {/* Circular image */}
            <Box sx={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
              <Box
                sx={{
                  width: { xs: 270, sm: 360, md: 420 },
                  height: { xs: 270, sm: 360, md: 420 },
                  borderRadius: '50%',
                  overflow: 'hidden',
                  border: `5px solid ${ACCENT}`,
                  flexShrink: 0,
                }}
              >
                <Box
                  component="img"
                  src={FEATURE_IMG}
                  alt="Вкусная еда UniFood"
                  sx={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </Box>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* ── QUOTE SECTION ───────────────────────────────────── */}
      <Box
        sx={{
          bgcolor: NAVY,
          py: { xs: 10, md: 16 },
          px: { xs: 3, md: 8 },
          textAlign: 'center',
        }}
      >
        <Typography
          sx={{
            fontFamily: "'Playfair Display', serif",
            fontStyle: 'italic',
            fontSize: { xs: '1.8rem', sm: '2.4rem', md: '3rem' },
            color: WHITE,
            lineHeight: 1.4,
            maxWidth: 860,
            mx: 'auto',
          }}
        >
          «В очередях мы теряем часы жизни.
          <br />Но обед в UniFood —
          <br />
          <Box component="span" sx={{ color: ACCENT }}>потерять точно не придётся.»</Box>
        </Typography>
      </Box>

      {/* ── STEPS SECTION ───────────────────────────────────── */}
      <Box sx={{ bgcolor: LIGHT, py: { xs: 8, md: 14 } }}>
        <Container maxWidth="lg">
          <Typography
            sx={{
              fontFamily: "'Bebas Neue', sans-serif",
              fontSize: { xs: '2.2rem', md: '3rem' },
              color: NAVY,
              textAlign: 'center',
              letterSpacing: 2,
              mb: 8,
            }}
          >
            КАК ЭТО РАБОТАЕТ?
          </Typography>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
              gap: 4,
            }}
          >
            {[
              { num: '01', label: 'Выбирайте', desc: 'Просматривайте меню и выбирайте любимые блюда', img: STEP1_IMG },
              { num: '02', label: 'Заказывайте', desc: 'Оформляйте заказ онлайн в пару кликов', img: STEP2_IMG },
              { num: '03', label: 'Забирайте', desc: 'Получайте горячий заказ без очередей', img: STEP3_IMG },
            ].map((step) => (
              <Box key={step.num} sx={{ textAlign: 'center' }}>
                <Box
                  sx={{
                    width: '100%',
                    height: 220,
                    borderRadius: '12px',
                    overflow: 'hidden',
                    mb: 3,
                    border: `1px solid ${ACCENT}30`,
                  }}
                >
                  <Box
                    component="img"
                    src={step.img}
                    alt={step.label}
                    sx={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1.5, mb: 1 }}>
                  <Box
                    sx={{
                      bgcolor: BLUE,
                      color: WHITE,
                      fontFamily: "'Bebas Neue', sans-serif",
                      fontSize: '0.85rem',
                      letterSpacing: 2,
                      px: 2,
                      py: 0.4,
                      borderRadius: '4px',
                    }}
                  >
                    ШАГ {step.num}
                  </Box>
                  <Typography
                    sx={{
                      fontFamily: "'Bebas Neue', sans-serif",
                      fontSize: '1.3rem',
                      color: NAVY,
                      letterSpacing: 1.5,
                    }}
                  >
                    {step.label.toUpperCase()}
                  </Typography>
                </Box>
                <Typography sx={{ fontSize: '0.9rem', color: NAVY, opacity: 0.6, maxWidth: 240, mx: 'auto', lineHeight: 1.7 }}>
                  {step.desc}
                </Typography>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>

      {/* ── GIANT BRAND NAME ────────────────────────────────── */}
      <Box
        sx={{
          bgcolor: NAVY,
          borderTop: `3px solid ${ACCENT}`,
          py: { xs: 2, md: 3 },
          overflow: 'hidden',
          textAlign: 'center',
        }}
      >
        <Typography
          sx={{
            fontFamily: "'Bebas Neue', sans-serif",
            fontSize: { xs: '18vw', md: '15vw' },
            color: ACCENT,
            lineHeight: 0.85,
            letterSpacing: '0.02em',
            userSelect: 'none',
            opacity: 0.85,
          }}
        >
          UNIFOOD
        </Typography>
      </Box>

      {/* ── FOOTER ──────────────────────────────────────────── */}
      <Box
        sx={{
          bgcolor: NAVY,
          borderTop: `1px solid rgba(255,255,255,0.08)`,
          py: 4,
          px: 4,
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 2,
        }}
      >
        <Typography sx={{ fontFamily: "'Bebas Neue', sans-serif", fontSize: '1.3rem', color: WHITE, letterSpacing: 3 }}>
          UNIFOOD
        </Typography>
        <Typography sx={{ fontSize: '0.85rem', color: WHITE, opacity: 0.45 }}>
          © 2026 UniFood. Сделано с любовью для студентов.
        </Typography>
        <Box sx={{ display: 'flex', gap: 3 }}>
          {[{ to: '/menu', label: 'Меню' }, { to: '/profile', label: 'Профиль' }].map(l => (
            <Typography
              key={l.to}
              component={Link}
              to={l.to}
              sx={{
                textDecoration: 'none',
                color: WHITE,
                opacity: 0.55,
                fontSize: '0.9rem',
                '&:hover': { opacity: 1 },
              }}
            >
              {l.label}
            </Typography>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default HomePage;
