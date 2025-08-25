import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { themes, Theme, defaultTheme } from '../themes';

interface ThemeContextType {
  currentTheme: string;
  theme: Theme;
  setTheme: (themeName: string) => void;
  availableThemes: string[];
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState<string>(() => {
    // Try to get theme from localStorage, fallback to default
    const savedTheme = localStorage.getItem('banking-agent-theme');
    return savedTheme && themes[savedTheme] ? savedTheme : defaultTheme;
  });

  const setTheme = (themeName: string) => {
    if (themes[themeName]) {
      setCurrentTheme(themeName);
      localStorage.setItem('banking-agent-theme', themeName);
    }
  };

  const theme = themes[currentTheme];
  const availableThemes = Object.keys(themes);

  // Apply theme to document body
  useEffect(() => {
    document.body.style.backgroundColor = theme.colors.background;
    document.body.style.color = theme.colors.text;
    document.body.style.fontFamily = theme.fonts.primary;
    document.body.setAttribute('data-theme', currentTheme);
  }, [theme, currentTheme]);

  const value: ThemeContextType = {
    currentTheme,
    theme,
    setTheme,
    availableThemes
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};
