import { ReactNode, useEffect, useRef, useState } from 'react';
import { CompactCharCounter } from './CharacterCounter';

interface PostPreviewModalProps {
    isOpen: boolean;
    onClose: () => void;
    postContent: string;
    imageUrl?: string | null;
    onPublish?: () => void;
    isPublishing?: boolean;
    testMode?: boolean;
}

export function PostPreviewModal({
    isOpen,
    onClose,
    postContent,
    imageUrl,
    onPublish,
    isPublishing = false,
    testMode = true
}: PostPreviewModalProps) {
    const modalRef = useRef<HTMLDivElement>(null);

    // Close on escape key
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden';
        }
        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    // Format post content with line breaks and hashtag highlighting
    const formatContent = (text: string) => {
        // Split by lines and process
        return text.split('\n').map((line, i) => {
            // Highlight hashtags
            const parts = line.split(/(#\w+)/g);
            return (
                <span key={i}>
                    {parts.map((part, j) =>
                        part.startsWith('#') ? (
                            <span key={j} className="text-blue-600 dark:text-blue-400 hover:underline cursor-pointer">
                                {part}
                            </span>
                        ) : (
                            <span key={j}>{part}</span>
                        )
                    )}
                    {i < text.split('\n').length - 1 && <br />}
                </span>
            );
        });
    };

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm scale-in"
            onClick={(e) => e.target === e.currentTarget && onClose()}
        >
            <div
                ref={modalRef}
                className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-hidden scale-in"
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Preview Post
                    </h3>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
                    >
                        <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* LinkedIn-style post preview */}
                <div className="p-4 overflow-y-auto max-h-[60vh]">
                    <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
                        {/* Post author header */}
                        <div className="flex items-start gap-3 mb-4">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold">
                                You
                            </div>
                            <div className="flex-1">
                                <p className="font-semibold text-gray-900 dark:text-white">Your Name</p>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Just now • 🌐</p>
                            </div>
                            <div className="text-blue-600">
                                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z" />
                                </svg>
                            </div>
                        </div>

                        {/* Post content */}
                        <div className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">
                            {formatContent(postContent)}
                        </div>

                        {/* Image preview if available */}
                        {imageUrl && (
                            <div className="mt-4 rounded-lg overflow-hidden">
                                <img
                                    src={imageUrl}
                                    alt="Post image"
                                    className="w-full h-auto max-h-64 object-cover"
                                />
                            </div>
                        )}

                        {/* Engagement bar (mock) */}
                        <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
                            <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 text-sm">
                                <span>👍 0 reactions</span>
                                <span>0 comments • 0 reposts</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                    <div className="flex items-center justify-between mb-3">
                        <CompactCharCounter text={postContent} />
                        {testMode && (
                            <span className="text-xs text-orange-500 font-medium">
                                🧪 Test Mode - Won't actually post
                            </span>
                        )}
                    </div>
                    <div className="flex gap-3">
                        <button
                            onClick={onClose}
                            className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                        >
                            Edit Post
                        </button>
                        <button
                            onClick={onPublish}
                            disabled={isPublishing || postContent.length > 3000}
                            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 btn-press"
                        >
                            {isPublishing ? (
                                <>
                                    <span className="animate-spin">⏳</span>
                                    Publishing...
                                </>
                            ) : (
                                <>
                                    <span>🚀</span>
                                    {testMode ? 'Test Publish' : 'Publish Now'}
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
