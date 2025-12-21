import React from 'react';

interface SkipToContentProps {
    targetId?: string;
    label?: string;
}

/**
 * SkipToContent component for accessibility.
 * Allows keyboard users to skip navigation and go directly to main content.
 */
const SkipToContent: React.FC<SkipToContentProps> = ({
    targetId = 'main-content',
    label = 'Skip to main content',
}) => {
    return (
        <a
            href={`#${targetId}`}
            className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
            {label}
        </a>
    );
};

export default SkipToContent;
