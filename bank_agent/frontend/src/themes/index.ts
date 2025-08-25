export interface Theme {
  name: string;
  description: string;
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    success: string;
    error: string;
    warning: string;
    info: string;
    primaryDark: string;
    hover: string;
  };
  fonts: {
    primary: string;
    monospace: string;
  };
  effects: {
    glow: string;
    shadow: string;
    hoverGlow: string;
  };
}

export const themes: { [key: string]: Theme } = {
  matrix: {
    name: "Matrix",
    description: "Dark theme with green glow effects",
    colors: {
      primary: "#00ff00",
      secondary: "#00cc00",
      background: "#000000",
      surface: "rgba(0, 0, 0, 0.8)",
      text: "#00ff00",
      textSecondary: "rgba(0, 255, 0, 0.7)",
      border: "#00ff00",
      success: "#00ff00",
      error: "#ff4444",
      warning: "#ffaa00",
      info: "#00ff00",
      primaryDark: "#00cc00",
      hover: "rgba(0, 255, 0, 0.1)"
    },
    fonts: {
      primary: "Courier New, monospace",
      monospace: "Courier New, monospace"
    },
    effects: {
      glow: "0 0 20px rgba(0, 255, 0, 0.6)",
      shadow: "0 0 10px rgba(0, 255, 0, 0.3)",
      hoverGlow: "0 0 30px rgba(0, 255, 0, 0.8)"
    }
  },
  vibrant: {
    name: "Vibrant",
    description: "Bright, colorful modern theme",
    colors: {
      primary: "#ff6b6b",
      secondary: "#4ecdc4",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      surface: "rgba(255, 255, 255, 0.4)",
      text: "#1a1a1a",
      textSecondary: "#4a4a4a",
      border: "#e74c3c",
      success: "#27ae60",
      error: "#e74c3c",
      warning: "#f39c12",
      info: "#3498db",
      primaryDark: "#e74c3c",
      hover: "rgba(255, 107, 107, 0.1)"
    },
    fonts: {
      primary: "Poppins, -apple-system, BlinkMacSystemFont, sans-serif",
      monospace: "Fira Code, Consolas, Monaco, monospace"
    },
    effects: {
      glow: "0 8px 32px rgba(255, 107, 107, 0.3)",
      shadow: "0 4px 16px rgba(0, 0, 0, 0.1)",
      hoverGlow: "0 12px 40px rgba(255, 107, 107, 0.4)"
    }
  },
  sunset: {
    name: "Sunset",
    description: "Warm orange and purple gradient",
    colors: {
      primary: "#ff8a65",
      secondary: "#ff7043",
      background: "linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%)",
      surface: "rgba(255, 255, 255, 0.5)",
      text: "#1a1a1a",
      textSecondary: "#4a4a4a",
      border: "#ff5722",
      success: "#4caf50",
      error: "#f44336",
      warning: "#ff9800",
      info: "#2196f3",
      primaryDark: "#e64a19",
      hover: "rgba(255, 138, 101, 0.1)"
    },
    fonts: {
      primary: "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
      monospace: "JetBrains Mono, Consolas, Monaco, monospace"
    },
    effects: {
      glow: "0 8px 32px rgba(255, 138, 101, 0.3)",
      shadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
      hoverGlow: "0 12px 40px rgba(255, 138, 101, 0.4)"
    }
  },
  ocean: {
    name: "Ocean",
    description: "Cool blue and teal theme",
    colors: {
      primary: "#00bcd4",
      secondary: "#009688",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      surface: "rgba(255, 255, 255, 0.5)",
      text: "#1a1a1a",
      textSecondary: "#4a4a4a",
      border: "#00acc1",
      success: "#4caf50",
      error: "#f44336",
      warning: "#ff9800",
      info: "#2196f3",
      primaryDark: "#0097a7",
      hover: "rgba(0, 188, 212, 0.1)"
    },
    fonts: {
      primary: "Nunito, -apple-system, BlinkMacSystemFont, sans-serif",
      monospace: "Source Code Pro, Consolas, Monaco, monospace"
    },
    effects: {
      glow: "0 8px 32px rgba(0, 188, 212, 0.3)",
      shadow: "0 4px 16px rgba(0, 0, 0, 0.1)",
      hoverGlow: "0 12px 40px rgba(0, 188, 212, 0.4)"
    }
  },
  corporate: {
    name: "Corporate",
    description: "Clean, professional blue theme",
    colors: {
      primary: "#1976d2",
      secondary: "#1565c0",
      background: "#f5f5f5",
      surface: "rgba(255, 255, 255, 0.7)",
      text: "#1a1a1a",
      textSecondary: "#4a4a4a",
      border: "#e0e0e0",
      success: "#2e7d32",
      error: "#d32f2f",
      warning: "#ed6c02",
      info: "#0288d1",
      primaryDark: "#1565c0",
      hover: "rgba(25, 118, 210, 0.1)"
    },
    fonts: {
      primary: "Roboto, -apple-system, BlinkMacSystemFont, sans-serif",
      monospace: "Consolas, Monaco, 'Courier New', monospace"
    },
    effects: {
      glow: "0 4px 20px rgba(25, 118, 210, 0.15)",
      shadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
      hoverGlow: "0 6px 25px rgba(25, 118, 210, 0.25)"
    }
  },
  readable: {
    name: "Readable",
    description: "High contrast, accessible design",
    colors: {
      primary: "#000000",
      secondary: "#333333",
      background: "#ffffff",
      surface: "rgba(250, 250, 250, 0.8)",
      text: "#000000",
      textSecondary: "#555555",
      border: "#000000",
      success: "#006600",
      error: "#cc0000",
      warning: "#cc6600",
      info: "#0066cc",
      primaryDark: "#000000",
      hover: "rgba(0, 0, 0, 0.1)"
    },
    fonts: {
      primary: "Arial, Helvetica, sans-serif",
      monospace: "Courier New, monospace"
    },
    effects: {
      glow: "0 2px 8px rgba(0, 0, 0, 0.2)",
      shadow: "0 1px 4px rgba(0, 0, 0, 0.1)",
      hoverGlow: "0 4px 12px rgba(0, 0, 0, 0.3)"
    }
  }
};

export const defaultTheme = "corporate";
