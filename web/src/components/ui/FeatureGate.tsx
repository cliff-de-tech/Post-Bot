/**
 * FeatureGate Component
 * 
 * Wraps Pro/Team features with a "Coming Soon" overlay for free tier users.
 * Used to indicate features that are not yet available but will be in the future.
 */

import React from 'react';

interface FeatureGateProps {
  feature: 'scheduling' | 'analytics' | 'templates' | 'unlimited';
  tier?: 'pro' | 'team';
  isLocked?: boolean;
  children: React.ReactNode;
  showOverlay?: boolean;
}

const featureDescriptions: Record<string, { title: string; description: string }> = {
  scheduling: {
    title: 'Scheduled Posting',
    description: 'Queue posts for optimal engagement times. Coming with Pro tier.',
  },
  analytics: {
    title: 'Full Analytics',
    description: 'View detailed engagement metrics and insights. Coming with Pro tier.',
  },
  templates: {
    title: 'All AI Templates',
    description: 'Access Build-in-Public, Thought Leadership, and more templates.',
  },
  unlimited: {
    title: 'Unlimited Posts',
    description: 'Remove daily limits and post as much as you want.',
  },
};

export default function FeatureGate({
  feature,
  tier = 'pro',
  isLocked = true,
  children,
  showOverlay = true,
}: FeatureGateProps) {
  const featureInfo = featureDescriptions[feature] || {
    title: 'Pro Feature',
    description: 'This feature is coming soon.',
  };

  if (!isLocked) {
    return <>{children}</>;
  }

  return (
    <div className="relative">
      {/* Content with reduced opacity */}
      <div className={showOverlay ? 'opacity-40 pointer-events-none select-none blur-[1px]' : ''}>
        {children}
      </div>

      {/* Overlay */}
      {showOverlay && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/5 dark:bg-white/5 backdrop-blur-[2px] rounded-xl">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 max-w-xs text-center">
            {/* Lock Icon */}
            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
              <svg
                className="w-6 h-6 text-blue-600 dark:text-blue-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </div>

            {/* Feature Name */}
            <h3 className="font-bold text-gray-900 dark:text-white mb-2">
              {featureInfo.title}
            </h3>

            {/* Description */}
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              {featureInfo.description}
            </p>

            {/* Coming Soon Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded-full text-sm font-medium">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {tier === 'pro' ? 'Pro' : 'Team'} • Coming Soon
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Inline badge component for locked features in lists
export function LockedBadge({ tier = 'pro' }: { tier?: 'pro' | 'team' }) {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-500 text-xs rounded-full">
      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
        />
      </svg>
      {tier === 'pro' ? 'Pro' : 'Team'}
    </span>
  );
}
