/**
 * UsageCounter Component
 * 
 * Displays the user's current usage (posts today) with a progress bar,
 * tier badge, and upgrade CTA for free tier users.
 */

import React, { useState, useEffect } from 'react';

interface UsageData {
    tier: string;
    posts_today: number;
    posts_limit: number;
    posts_remaining: number;
    scheduled_count: number;
    scheduled_limit: number;
    scheduled_remaining: number;
    resets_in_seconds: number;
    resets_at: string | null;
}

interface UsageCounterProps {
    usage: UsageData | null;
    compact?: boolean;
    onUpgradeClick?: () => void;
}

function formatTimeRemaining(seconds: number): string {
    if (seconds <= 0) return 'now';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
}

// Tier badge colors
const tierColors: Record<string, { bg: string; text: string; border: string }> = {
    free: {
        bg: 'bg-gray-100 dark:bg-gray-800',
        text: 'text-gray-700 dark:text-gray-300',
        border: 'border-gray-300 dark:border-gray-600'
    },
    pro: {
        bg: 'bg-gradient-to-r from-blue-500 to-purple-500',
        text: 'text-white',
        border: 'border-transparent'
    },
    team: {
        bg: 'bg-gradient-to-r from-emerald-500 to-teal-500',
        text: 'text-white',
        border: 'border-transparent'
    }
};

export default function UsageCounter({ usage, compact = false, onUpgradeClick }: UsageCounterProps) {
    const [timeRemaining, setTimeRemaining] = useState<number>(usage?.resets_in_seconds || 0);

    useEffect(() => {
        if (!usage?.resets_in_seconds) return;

        setTimeRemaining(usage.resets_in_seconds);

        const interval = setInterval(() => {
            setTimeRemaining(prev => Math.max(0, prev - 60));
        }, 60000); // Update every minute

        return () => clearInterval(interval);
    }, [usage?.resets_in_seconds]);

    // Loading state
    if (!usage) {
        return (
            <div className="bg-white dark:bg-gray-800/50 rounded-xl p-4 border border-gray-200 dark:border-gray-700 animate-pulse">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-3"></div>
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
            </div>
        );
    }

    const tier = usage.tier.toLowerCase();
    const colors = tierColors[tier] || tierColors.free;
    const isUnlimited = usage.posts_limit === -1;
    const percentUsed = isUnlimited ? 0 : (usage.posts_today / usage.posts_limit) * 100;
    const isLow = !isUnlimited && usage.posts_remaining <= 3;
    const isExhausted = !isUnlimited && usage.posts_remaining === 0;

    // Compact version for header
    if (compact) {
        return (
            <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${colors.bg} ${colors.text} border ${colors.border}`}>
                    {usage.tier.toUpperCase()}
                </span>
                {!isUnlimited && (
                    <span className={`text-sm font-medium ${isExhausted ? 'text-red-500' : isLow ? 'text-yellow-500' : 'text-gray-600 dark:text-gray-400'}`}>
                        {usage.posts_remaining}/{usage.posts_limit}
                    </span>
                )}
            </div>
        );
    }

    return (
        <div className="bg-white dark:bg-gray-800/50 rounded-xl p-5 border border-gray-200 dark:border-gray-700 shadow-sm">
            {/* Header with Tier and Upgrade */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    {/* Tier Badge */}
                    <span className={`px-3 py-1 text-xs font-bold rounded-full ${colors.bg} ${colors.text} border ${colors.border} uppercase tracking-wide`}>
                        {usage.tier} Plan
                    </span>

                    {/* Reset timer for limited tiers */}
                    {!isUnlimited && timeRemaining > 0 && (
                        <span className="text-xs text-gray-400 dark:text-gray-500 flex items-center gap-1">
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                            Resets in {formatTimeRemaining(timeRemaining)}
                        </span>
                    )}
                </div>

                {/* Upgrade CTA for free tier */}
                {tier === 'free' && (
                    <button
                        onClick={onUpgradeClick}
                        className="px-3 py-1.5 text-xs font-semibold bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full hover:from-blue-600 hover:to-purple-600 transition-all shadow-sm hover:shadow-md flex items-center gap-1"
                    >
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                        </svg>
                        Upgrade to Pro
                    </button>
                )}
            </div>

            {/* Usage Stats */}
            {isUnlimited ? (
                // Unlimited tier display
                <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400 font-medium">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Unlimited posts • No restrictions
                </div>
            ) : (
                // Limited tier display with progress bar
                <div className="space-y-3">
                    {/* Posts Today */}
                    <div>
                        <div className="flex items-center justify-between mb-1.5">
                            <span className="text-sm text-gray-600 dark:text-gray-400">Posts Today</span>
                            <span className={`text-sm font-bold ${isExhausted ? 'text-red-500' : isLow ? 'text-yellow-500' : 'text-gray-900 dark:text-white'
                                }`}>
                                {usage.posts_today} / {usage.posts_limit}
                            </span>
                        </div>

                        {/* Progress bar */}
                        <div className="h-2.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all duration-500 ${isExhausted
                                        ? 'bg-red-500'
                                        : isLow
                                            ? 'bg-gradient-to-r from-yellow-400 to-orange-500'
                                            : 'bg-gradient-to-r from-blue-500 to-purple-500'
                                    }`}
                                style={{ width: `${Math.min(100, percentUsed)}%` }}
                            />
                        </div>
                    </div>

                    {/* Scheduled Posts */}
                    <div className="flex items-center justify-between text-sm pt-2 border-t border-gray-100 dark:border-gray-700">
                        <span className="text-gray-500 dark:text-gray-400 flex items-center gap-1.5">
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            Scheduled
                        </span>
                        <span className={`font-medium ${usage.scheduled_remaining === 0
                                ? 'text-red-500'
                                : 'text-gray-700 dark:text-gray-300'
                            }`}>
                            {usage.scheduled_count} / {usage.scheduled_limit}
                        </span>
                    </div>
                </div>
            )}

            {/* Exhausted Warning */}
            {isExhausted && (
                <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <div className="flex items-start gap-2 text-red-600 dark:text-red-400 text-sm">
                        <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <div>
                            <span className="font-medium">Daily limit reached.</span>
                            <span className="block text-red-500 dark:text-red-400/80">
                                New posts available in {formatTimeRemaining(timeRemaining)}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

