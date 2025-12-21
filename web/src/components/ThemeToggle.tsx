import React, { useState } from 'react';
import { useTheme } from './ThemeProvider';

export default function ThemeToggle() {
  const { theme, toggle } = useTheme();
  const [isAnimating, setIsAnimating] = useState(false);

  const handleToggle = () => {
    setIsAnimating(true);
    toggle();
    // Reset animation state after transition
    setTimeout(() => setIsAnimating(false), 300);
  };

  return (
    <button
      onClick={handleToggle}
      aria-label="Toggle theme"
      className="relative flex items-center gap-2 px-3 py-2 rounded-lg bg-white/10 dark:bg-white/5 text-gray-700 dark:text-purple-200 hover:bg-white/20 dark:hover:bg-white/10 transition-all duration-300 overflow-hidden group"
    >
      {/* Background glow effect */}
      <div className={`absolute inset-0 bg-gradient-to-r ${theme === 'dark'
          ? 'from-indigo-500/20 via-purple-500/20 to-pink-500/20'
          : 'from-yellow-400/20 via-orange-400/20 to-rose-400/20'
        } opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />

      {/* Icon container with rotation animation */}
      <div className={`relative transition-transform duration-300 ${isAnimating ? 'rotate-180 scale-110' : ''}`}>
        {theme === 'dark' ? (
          <svg className="w-5 h-5 text-purple-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
          </svg>
        ) : (
          <svg className="w-5 h-5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m8-9h1M3 12H2m15.364 6.364l.707.707M6.343 6.343l-.707-.707m12.728 0l.707-.707M6.343 17.657l-.707.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
          </svg>
        )}
      </div>

      <span className="relative text-sm font-medium transition-all duration-300">
        {theme === 'dark' ? 'Dark' : 'Light'}
      </span>
    </button>
  );
}

