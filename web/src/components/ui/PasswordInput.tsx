import React, { useState, InputHTMLAttributes, forwardRef } from 'react';

interface PasswordInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
    error?: string;
    label?: string;
    helperText?: string;
}

/**
 * PasswordInput component with visibility toggle.
 * Provides better UX for entering API keys and passwords.
 */
const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
    ({ error, label, helperText, className = '', id, ...props }, ref) => {
        const [isVisible, setIsVisible] = useState(false);
        const inputId = id || `password-input-${Math.random().toString(36).substr(2, 9)}`;
        const errorId = `${inputId}-error`;
        const helperId = `${inputId}-helper`;

        return (
            <div className="group">
                {label && (
                    <label
                        htmlFor={inputId}
                        className="block text-sm font-medium text-gray-700 dark:text-purple-200 mb-2"
                    >
                        {label}
                    </label>
                )}
                <div className="relative">
                    <input
                        ref={ref}
                        id={inputId}
                        type={isVisible ? 'text' : 'password'}
                        className={`w-full px-4 py-3 pr-12 bg-white border dark:bg-white/5 dark:border-white/10 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-purple-300/50 focus:ring-2 focus:border-transparent transition-all duration-300 group-hover:border-gray-400 dark:group-hover:border-white/20 ${error
                                ? 'border-red-500/50 focus:ring-red-500'
                                : 'border-gray-300 dark:border-white/10 focus:ring-purple-500'
                            } ${className}`}
                        aria-invalid={error ? 'true' : 'false'}
                        aria-describedby={error ? errorId : helperText ? helperId : undefined}
                        {...props}
                    />
                    <button
                        type="button"
                        onClick={() => setIsVisible(!isVisible)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 rounded"
                        aria-label={isVisible ? 'Hide password' : 'Show password'}
                    >
                        {isVisible ? (
                            <svg
                                className="w-5 h-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                aria-hidden="true"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                                />
                            </svg>
                        ) : (
                            <svg
                                className="w-5 h-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                aria-hidden="true"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                />
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                                />
                            </svg>
                        )}
                    </button>
                </div>
                {error && (
                    <p id={errorId} className="text-red-400 text-sm mt-2 flex items-center" role="alert">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                            <path
                                fillRule="evenodd"
                                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                                clipRule="evenodd"
                            />
                        </svg>
                        {error}
                    </p>
                )}
                {helperText && !error && (
                    <p id={helperId} className="text-gray-500 dark:text-gray-400 text-sm mt-2">
                        {helperText}
                    </p>
                )}
            </div>
        );
    }
);

PasswordInput.displayName = 'PasswordInput';

export default PasswordInput;
