/**
 * TierBadge Component
 * 
 * Compact badge showing user's current tier (Free/Pro/Team)
 * Placed in the header next to theme toggle
 */

import React from 'react';

interface TierBadgeProps {
    tier: string;
    onClick?: () => void;
}

const tierConfig: Record<string, { label: string; colors: string; icon: string }> = {
    free: {
        label: 'Free',
        colors: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 border-gray-300 dark:border-gray-600',
        icon: '⚡'
    },
    pro: {
        label: 'Pro',
        colors: 'bg-gradient-to-r from-blue-500 to-purple-500 text-white border-transparent',
        icon: '🚀'
    },
    team: {
        label: 'Team',
        colors: 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white border-transparent',
        icon: '👥'
    }
};

export default function TierBadge({ tier, onClick }: TierBadgeProps) {
    const config = tierConfig[tier.toLowerCase()] || tierConfig.free;

    return (
        <button
            onClick={onClick}
            className={`px-3 py-1.5 text-xs font-bold rounded-full border ${config.colors} hover:opacity-90 transition-all flex items-center gap-1.5`}
            title={`Current plan: ${config.label}`}
        >
            <span>{config.icon}</span>
            <span>{config.label}</span>
        </button>
    );
}
