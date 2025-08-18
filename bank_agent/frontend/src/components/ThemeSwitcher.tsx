import React from 'react';
import {
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Chip
} from '@mui/material';
import { Palette as PaletteIcon } from '@mui/icons-material';
import { useTheme } from '../contexts/ThemeContext';
import { themes } from '../themes';

const ThemeSwitcher: React.FC = () => {
  const { currentTheme, setTheme, availableThemes } = useTheme();


  const handleThemeChange = (event: any) => {
    setTheme(event.target.value);
  };

  const currentThemeData = themes[currentTheme];

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1
      }}
    >
      <PaletteIcon 
        sx={{ 
          color: currentThemeData.colors.primary,
          fontSize: 28
        }} 
      />
      <FormControl size="medium" sx={{ minWidth: 180 }}>
        <InputLabel 
          sx={{ 
            color: currentThemeData.colors.textSecondary,
            fontFamily: currentThemeData.fonts.primary,
            fontSize: '1.1rem',
            fontWeight: 600
          }}
        >
          Theme
        </InputLabel>
        <Select
          value={currentTheme}
          onChange={handleThemeChange}
          label="Theme"
          sx={{
            color: currentThemeData.colors.text,
            fontFamily: currentThemeData.fonts.primary,
            fontSize: '1.1rem',
            fontWeight: 600,
            backgroundColor: currentThemeData.colors.surface,
            border: `1px solid ${currentThemeData.colors.border}`,
            borderRadius: 1,
            height: '48px',
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: currentThemeData.colors.border,
            },
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: currentThemeData.colors.primary,
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: currentThemeData.colors.primary,
            },
            '& .MuiSvgIcon-root': {
              color: currentThemeData.colors.textSecondary,
            }
          }}
        >
          {availableThemes.map((themeName) => {
            const theme = themes[themeName];
            return (
              <MenuItem 
                key={themeName} 
                value={themeName}
                sx={{
                  fontFamily: theme.fonts.primary,
                  color: theme.colors.text,
                  backgroundColor: theme.colors.surface,
                  '&:hover': {
                    backgroundColor: theme.colors.background,
                  },
                  '&.Mui-selected': {
                    backgroundColor: theme.colors.primary,
                    color: theme.colors.surface,
                    '&:hover': {
                      backgroundColor: theme.colors.primary,
                    }
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    label={theme.name}
                    size="medium"
                    sx={{
                      backgroundColor: theme.colors.primary,
                      color: theme.colors.surface,
                      fontFamily: theme.fonts.primary,
                      fontSize: '1rem',
                      fontWeight: 700,
                      height: 28
                    }}
                  />
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      color: 'inherit',
                      fontFamily: theme.fonts.primary,
                      opacity: 0.8,
                      fontSize: '1rem'
                    }}
                  >
                    {theme.description}
                  </Typography>
                </Box>
              </MenuItem>
            );
          })}
        </Select>
      </FormControl>
    </Box>
  );
};

export default ThemeSwitcher;
