/**
 * AnimatedBackground Component
 * 
 * Beautiful animated gradient orbs (purple/blue) matching onboarding theme.
 * Add to any page for consistent premium look.
 */

import React from 'react';
import InteractiveBackground from './InteractiveBackground';

interface AnimatedBackgroundProps {
    /** Intensity of colors (lower = more subtle) */
    intensity?: 'subtle' | 'normal' | 'vibrant';
    /** Animation style */
    variant?: 'blobs' | 'antigravity' | 'interactive';
    /** Show fixed position (for layout wrapper) or absolute (for page) */
    fixed?: boolean;
}

export default function AnimatedBackground({
    intensity = 'normal',
    variant = 'blobs',
    fixed = true
}: AnimatedBackgroundProps) {
    const opacityMap = {
        subtle: 'opacity-30',
        normal: 'opacity-40',
        vibrant: 'opacity-60'
    };

    const opacity = opacityMap[intensity];

    // Variant 'interactive' now combines blobs + interactive particles
    const showInteractive = variant === 'interactive';

    // We removed 'antigravity' floating particles block to simplify merging variants

    return (
        <div
            className={`${fixed ? 'fixed' : 'absolute'} inset-0 pointer-events-none overflow-hidden z-0`}
            aria-hidden="true"
        >
            {/* Standard Blobs Background (Visible for all variants including interactive) */}

            {/* Top right blob - Purple */}
            <div
                className={`absolute -top-[20%] -right-[10%] w-[70vw] h-[70vw] max-w-[800px] max-h-[800px] 
                    bg-purple-500 dark:bg-purple-600 rounded-full blur-3xl 
                    animate-blob ${opacity}`}
            />

            {/* Bottom left blob - Blue */}
            <div
                className={`absolute -bottom-[20%] -left-[10%] w-[70vw] h-[70vw] max-w-[800px] max-h-[800px] 
                    bg-blue-500 dark:bg-blue-600 rounded-full blur-3xl 
                    animate-blob animation-delay-4000 ${opacity}`}
            />

            {/* Optional center accent - Pink (subtle) */}
            <div
                className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 
                    w-[50vw] h-[50vw] max-w-[600px] max-h-[600px] 
                    bg-pink-500/20 dark:bg-pink-600/20 rounded-full blur-3xl 
                    animate-blob animation-delay-2000 opacity-20`}
            />

            {/* Interactive Overlay */}
            {showInteractive && (
                <InteractiveBackground className="z-10" />
            )}
        </div>
    );
}
