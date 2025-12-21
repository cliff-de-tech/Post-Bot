import { useMemo } from 'react';

interface CharacterCounterProps {
    text: string;
    maxLength?: number;
    showWarningAt?: number;
    className?: string;
}

export function CharacterCounter({
    text,
    maxLength = 3000, // LinkedIn's limit
    showWarningAt = 2700,
    className = ''
}: CharacterCounterProps) {
    const count = text.length;
    const remaining = maxLength - count;
    const percentage = (count / maxLength) * 100;

    const status = useMemo(() => {
        if (count > maxLength) return 'error';
        if (count > showWarningAt) return 'warning';
        return 'normal';
    }, [count, maxLength, showWarningAt]);

    const statusColors = {
        normal: 'text-gray-500 dark:text-gray-400',
        warning: 'text-orange-500 dark:text-orange-400',
        error: 'text-red-500 dark:text-red-400'
    };

    const progressColors = {
        normal: 'bg-blue-500',
        warning: 'bg-orange-500',
        error: 'bg-red-500'
    };

    return (
        <div className={`flex items-center gap-3 ${className}`}>
            {/* Progress Ring */}
            <div className="relative w-8 h-8">
                <svg className="w-8 h-8 transform -rotate-90">
                    {/* Background circle */}
                    <circle
                        cx="16"
                        cy="16"
                        r="14"
                        stroke="currentColor"
                        strokeWidth="2"
                        fill="none"
                        className="text-gray-200 dark:text-gray-700"
                    />
                    {/* Progress circle */}
                    <circle
                        cx="16"
                        cy="16"
                        r="14"
                        stroke="currentColor"
                        strokeWidth="2"
                        fill="none"
                        strokeDasharray={`${Math.min(percentage, 100) * 0.88} 88`}
                        strokeLinecap="round"
                        className={progressColors[status]}
                    />
                </svg>
            </div>

            {/* Text counter */}
            <div className={`text-sm font-medium ${statusColors[status]}`}>
                {status === 'error' ? (
                    <span className="flex items-center gap-1">
                        <span className="animate-pulse">⚠️</span>
                        {Math.abs(remaining)} over limit
                    </span>
                ) : (
                    <span>{remaining.toLocaleString()} characters left</span>
                )}
            </div>
        </div>
    );
}

// Compact version for inline use
export function CompactCharCounter({
    text,
    maxLength = 3000
}: { text: string; maxLength?: number }) {
    const count = text.length;
    const isOver = count > maxLength;

    return (
        <span className={`text-xs font-mono ${isOver
                ? 'text-red-500 font-bold'
                : count > maxLength * 0.9
                    ? 'text-orange-500'
                    : 'text-gray-400'
            }`}>
            {count.toLocaleString()}/{maxLength.toLocaleString()}
        </span>
    );
}
