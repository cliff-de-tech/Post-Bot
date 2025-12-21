interface SkeletonProps {
    className?: string;
    variant?: 'text' | 'circular' | 'rectangular';
    width?: string | number;
    height?: string | number;
    count?: number;
}

export function Skeleton({
    className = '',
    variant = 'rectangular',
    width,
    height,
    count = 1
}: SkeletonProps) {
    const baseClasses = 'skeleton rounded animate-pulse';

    const variantClasses = {
        text: 'h-4 rounded',
        circular: 'rounded-full',
        rectangular: 'rounded-lg'
    };

    const style = {
        width: width ? (typeof width === 'number' ? `${width}px` : width) : undefined,
        height: height ? (typeof height === 'number' ? `${height}px` : height) : undefined,
    };

    if (count > 1) {
        return (
            <div className="space-y-2">
                {Array.from({ length: count }).map((_, i) => (
                    <div
                        key={i}
                        className={`${baseClasses} ${variantClasses[variant]} ${className}`}
                        style={style}
                    />
                ))}
            </div>
        );
    }

    return (
        <div
            className={`${baseClasses} ${variantClasses[variant]} ${className}`}
            style={style}
        />
    );
}

// Pre-built skeleton patterns for common use cases
export function CardSkeleton() {
    return (
        <div className="bg-white dark:bg-white/5 rounded-2xl p-6 border border-gray-100 dark:border-white/10">
            <div className="flex items-center gap-4 mb-4">
                <Skeleton variant="circular" width={48} height={48} />
                <div className="flex-1">
                    <Skeleton width="60%" height={16} className="mb-2" />
                    <Skeleton width="40%" height={12} />
                </div>
            </div>
            <Skeleton height={80} className="mb-4" />
            <div className="flex gap-2">
                <Skeleton width={80} height={32} />
                <Skeleton width={80} height={32} />
            </div>
        </div>
    );
}

export function ActivitySkeleton() {
    return (
        <div className="flex items-start gap-3 p-3 rounded-lg">
            <Skeleton variant="circular" width={36} height={36} />
            <div className="flex-1">
                <Skeleton width="80%" height={14} className="mb-2" />
                <Skeleton width="50%" height={12} />
            </div>
        </div>
    );
}

export function StatSkeleton() {
    return (
        <div className="bg-white dark:bg-white/5 rounded-xl p-4 border border-gray-100 dark:border-white/10">
            <Skeleton width={60} height={12} className="mb-2" />
            <Skeleton width={80} height={28} />
        </div>
    );
}
