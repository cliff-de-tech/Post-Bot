import { showToast } from '@/lib/toast';

interface ExportPost {
    content: string;
    createdAt?: string | number;
    status?: string;
    type?: string;
}

export function exportPostsAsMarkdown(posts: ExportPost[], filename = 'linkedin-posts') {
    const date = new Date().toISOString().split('T')[0];

    let markdown = `# LinkedIn Posts Export\n\nExported on: ${date}\nTotal posts: ${posts.length}\n\n---\n\n`;

    posts.forEach((post, index) => {
        const postDate = post.createdAt
            ? new Date(typeof post.createdAt === 'number' ? post.createdAt * 1000 : post.createdAt).toLocaleDateString()
            : 'Unknown date';

        markdown += `## Post ${index + 1}\n\n`;
        markdown += `**Date:** ${postDate}\n`;
        if (post.status) markdown += `**Status:** ${post.status}\n`;
        if (post.type) markdown += `**Type:** ${post.type}\n`;
        markdown += `\n${post.content}\n\n---\n\n`;
    });

    downloadFile(markdown, `${filename}-${date}.md`, 'text/markdown');
    showToast.success(`Exported ${posts.length} posts as Markdown`);
}

export function exportPostsAsJSON(posts: ExportPost[], filename = 'linkedin-posts') {
    const date = new Date().toISOString().split('T')[0];
    const data = {
        exportedAt: new Date().toISOString(),
        totalPosts: posts.length,
        posts: posts
    };

    downloadFile(JSON.stringify(data, null, 2), `${filename}-${date}.json`, 'application/json');
    showToast.success(`Exported ${posts.length} posts as JSON`);
}

export function exportPostsAsCSV(posts: ExportPost[], filename = 'linkedin-posts') {
    const date = new Date().toISOString().split('T')[0];

    // CSV header
    let csv = 'Content,Date,Status,Type\n';

    posts.forEach(post => {
        const postDate = post.createdAt
            ? new Date(typeof post.createdAt === 'number' ? post.createdAt * 1000 : post.createdAt).toISOString()
            : '';
        const content = `"${post.content.replace(/"/g, '""')}"`;
        csv += `${content},${postDate},${post.status || ''},${post.type || ''}\n`;
    });

    downloadFile(csv, `${filename}-${date}.csv`, 'text/csv');
    showToast.success(`Exported ${posts.length} posts as CSV`);
}

function downloadFile(content: string, filename: string, mimeType: string) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Export dropdown component
interface ExportDropdownProps {
    posts: ExportPost[];
    className?: string;
}

export function ExportDropdown({ posts, className = '' }: ExportDropdownProps) {
    const [isOpen, setIsOpen] = React.useState(false);

    if (posts.length === 0) return null;

    return (
        <div className={`relative ${className}`}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center gap-2"
            >
                <span>📥</span>
                Export
                <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {isOpen && (
                <div className="absolute top-full right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 z-50 scale-in overflow-hidden">
                    <button
                        onClick={() => { exportPostsAsMarkdown(posts); setIsOpen(false); }}
                        className="w-full px-4 py-3 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center gap-3"
                    >
                        <span>📝</span>
                        Export as Markdown
                    </button>
                    <button
                        onClick={() => { exportPostsAsJSON(posts); setIsOpen(false); }}
                        className="w-full px-4 py-3 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center gap-3"
                    >
                        <span>📦</span>
                        Export as JSON
                    </button>
                    <button
                        onClick={() => { exportPostsAsCSV(posts); setIsOpen(false); }}
                        className="w-full px-4 py-3 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center gap-3"
                    >
                        <span>📊</span>
                        Export as CSV
                    </button>
                </div>
            )}
        </div>
    );
}

// Need React for the component
import React from 'react';
