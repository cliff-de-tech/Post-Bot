import React from 'react';
import { Skeleton } from '@/components/ui/SkeletonLoader';

interface StatsProps {
    stats: {
        posts_generated: number;
        credits_remaining: number;
        posts_published: number;
    } | null;
    loading: boolean;
}

export const StatsOverview: React.FC<StatsProps> = ({ stats, loading }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8" role="region" aria-label="Dashboard statistics">
            {/* Credits Card */}
            <div className="bg-white dark:bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-gray-200 dark:border-white/10 shadow-sm hover:shadow-md transition-all">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-gray-600 dark:text-gray-400 font-medium" id="credits-label">Credits Remaining</h3>
                    <div className="p-2 bg-blue-50 dark:bg-blue-500/10 rounded-lg" aria-hidden="true">
                        <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                </div>
                {loading ? (
                    <Skeleton className="h-8 w-24" />
                ) : (
                    <div className="flex items-baseline gap-2" aria-labelledby="credits-label">
                        <span className="text-3xl font-bold text-gray-900 dark:text-white">{stats?.credits_remaining || 0}</span>
                        <span className="text-sm text-gray-500">/ 50</span>
                    </div>
                )}
            </div>

            {/* Generated Card */}
            <div className="bg-white dark:bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-gray-200 dark:border-white/10 shadow-sm hover:shadow-md transition-all">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-gray-600 dark:text-gray-400 font-medium" id="generated-label">Generated Posts</h3>
                    <div className="p-2 bg-purple-50 dark:bg-purple-500/10 rounded-lg" aria-hidden="true">
                        <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                    </div>
                </div>
                {loading ? (
                    <Skeleton className="h-8 w-16" />
                ) : (
                    <div className="flex items-baseline gap-2" aria-labelledby="generated-label">
                        <span className="text-3xl font-bold text-gray-900 dark:text-white">{stats?.posts_generated || 0}</span>
                        <span className="text-sm text-green-500 flex items-center" aria-label="12 percent increase">
                            <svg className="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                            </svg>
                            +12%
                        </span>
                    </div>
                )}
            </div>

            {/* Published Card */}
            <div className="bg-white dark:bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-gray-200 dark:border-white/10 shadow-sm hover:shadow-md transition-all">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-gray-600 dark:text-gray-400 font-medium" id="published-label">Published</h3>
                    <div className="p-2 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg" aria-hidden="true">
                        <svg className="w-6 h-6 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                </div>
                {loading ? (
                    <Skeleton className="h-8 w-16" />
                ) : (
                    <div className="flex items-baseline gap-2" aria-labelledby="published-label">
                        <span className="text-3xl font-bold text-gray-900 dark:text-white">{stats?.posts_published || 0}</span>
                        <span className="text-sm text-gray-500">this month</span>
                    </div>
                )}
            </div>
        </div>
    );
};

