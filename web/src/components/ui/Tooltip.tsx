import { ReactNode, useState } from 'react';

interface TooltipProps {
    content: string;
    children: ReactNode;
    position?: 'top' | 'bottom' | 'left' | 'right';
    delay?: number;
}

export function Tooltip({
    content,
    children,
    position = 'top',
    delay = 200
}: TooltipProps) {
    const [show, setShow] = useState(false);
    const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);

    const positionClasses = {
        top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
        bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
        left: 'right-full top-1/2 -translate-y-1/2 mr-2',
        right: 'left-full top-1/2 -translate-y-1/2 ml-2',
    };

    const arrowClasses = {
        top: 'top-full left-1/2 -translate-x-1/2 border-t-gray-900 border-l-transparent border-r-transparent border-b-transparent',
        bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-gray-900 border-l-transparent border-r-transparent border-t-transparent',
        left: 'left-full top-1/2 -translate-y-1/2 border-l-gray-900 border-t-transparent border-b-transparent border-r-transparent',
        right: 'right-full top-1/2 -translate-y-1/2 border-r-gray-900 border-t-transparent border-b-transparent border-l-transparent',
    };

    const handleMouseEnter = () => {
        const id = setTimeout(() => setShow(true), delay);
        setTimeoutId(id);
    };

    const handleMouseLeave = () => {
        if (timeoutId) clearTimeout(timeoutId);
        setShow(false);
    };

    return (
        <div
            className="relative inline-flex"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            {children}
            {show && (
                <div
                    className={`absolute z-50 px-3 py-2 text-xs font-medium text-white bg-gray-900 rounded-lg shadow-lg whitespace-nowrap scale-in ${positionClasses[position]}`}
                    role="tooltip"
                >
                    {content}
                    <div
                        className={`absolute w-0 h-0 border-4 ${arrowClasses[position]}`}
                    />
                </div>
            )}
        </div>
    );
}

// Quick info tooltip for help icons
export function InfoTooltip({ content }: { content: string }) {
    return (
        <Tooltip content={content} position="top">
            <span className="inline-flex items-center justify-center w-4 h-4 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 cursor-help transition-colors">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            </span>
        </Tooltip>
    );
}
