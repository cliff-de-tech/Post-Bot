import React from 'react';

interface SkeletonProps {
    className?: string;
}

/**
 * Base skeleton component with shimmer animation
 */
export const Skeleton: React.FC<SkeletonProps> = ({ className = '' }) => (
    <div
        className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded ${className}`}
        aria-hidden="true"
    />
);

/**
 * Skeleton for text lines
 */
export const SkeletonText: React.FC<{ lines?: number; className?: string }> = ({
    lines = 3,
    className = '',
}) => (
    <div className={`space-y-2 ${className}`} aria-hidden="true">
        {Array.from({ length: lines }).map((_, i) => (
            <Skeleton
                key={i}
                className={`h-4 ${i === lines - 1 ? 'w-3/4' : 'w-full'}`}
            />
        ))}
    </div>
);

/**
 * Skeleton for circular avatars
 */
export const SkeletonAvatar: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({
    size = 'md',
}) => {
    const sizeClasses = {
        sm: 'w-8 h-8',
        md: 'w-12 h-12',
        lg: 'w-16 h-16',
    };

    return (
        <Skeleton className={`${sizeClasses[size]} rounded-full`} />
    );
};

/**
 * Skeleton for stat cards in dashboard
 */
export const SkeletonStatCard: React.FC = () => (
    <div className="bg-white dark:bg-white/5 rounded-2xl p-6 border border-gray-100 dark:border-white/10" aria-hidden="true">
        <div className="flex items-center justify-between mb-4">
            <Skeleton className="w-10 h-10 rounded-xl" />
            <Skeleton className="w-16 h-6 rounded-full" />
        </div>
        <Skeleton className="h-8 w-20 mb-2" />
        <Skeleton className="h-4 w-32" />
    </div>
);

/**
 * Skeleton for activity feed items
 */
export const SkeletonActivityItem: React.FC = () => (
    <div className="flex items-start gap-3 p-4 border border-gray-100 dark:border-white/10 rounded-xl" aria-hidden="true">
        <Skeleton className="w-10 h-10 rounded-xl flex-shrink-0" />
        <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
            <Skeleton className="h-3 w-1/4" />
        </div>
    </div>
);

/**
 * Skeleton for post preview card
 */
export const SkeletonPostCard: React.FC = () => (
    <div className="bg-white dark:bg-white/5 rounded-2xl p-6 border border-gray-100 dark:border-white/10" aria-hidden="true">
        <div className="flex items-center gap-3 mb-4">
            <SkeletonAvatar size="md" />
            <div className="space-y-2">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-24" />
            </div>
        </div>
        <SkeletonText lines={4} />
        <div className="mt-4 pt-4 border-t border-gray-100 dark:border-white/10 flex gap-4">
            <Skeleton className="h-8 w-16 rounded" />
            <Skeleton className="h-8 w-20 rounded" />
            <Skeleton className="h-8 w-16 rounded" />
        </div>
    </div>
);

/**
 * Skeleton for the entire dashboard layout
 */
export const SkeletonDashboard: React.FC = () => (
    <div className="space-y-8" aria-label="Loading dashboard" role="status">
        {/* Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
                <SkeletonStatCard key={i} />
            ))}
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Activity Feed */}
            <div className="space-y-4">
                <Skeleton className="h-6 w-32 mb-4" />
                {Array.from({ length: 3 }).map((_, i) => (
                    <SkeletonActivityItem key={i} />
                ))}
            </div>

            {/* Post Editor & Preview */}
            <div className="lg:col-span-2 space-y-8">
                <div className="bg-white dark:bg-white/5 rounded-2xl p-6 border border-gray-100 dark:border-white/10">
                    <Skeleton className="h-6 w-40 mb-6" />
                    <div className="space-y-4">
                        <Skeleton className="h-12 w-full rounded-xl" />
                        <Skeleton className="h-12 w-full rounded-xl" />
                        <div className="flex gap-4">
                            <Skeleton className="h-12 w-32 rounded-xl" />
                            <Skeleton className="h-12 w-32 rounded-xl" />
                        </div>
                    </div>
                </div>
                <SkeletonPostCard />
            </div>
        </div>
        <span className="sr-only">Loading...</span>
    </div>
);

export default {
    Skeleton,
    SkeletonText,
    SkeletonAvatar,
    SkeletonStatCard,
    SkeletonActivityItem,
    SkeletonPostCard,
    SkeletonDashboard,
};
