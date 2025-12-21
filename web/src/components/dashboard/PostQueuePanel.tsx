import { useState } from 'react';
import { CompactCharCounter } from '@/components/ui/CharacterCounter';
import { PostPreviewModal } from '@/components/ui/PostPreviewModal';
import { PostScheduler } from '@/components/ui/PostScheduler';
import { TemplateSelector } from '@/components/ui/PostTemplates';
import { usePublishShortcut, ShortcutHint } from '@/hooks/useKeyboardShortcuts';

interface Post {
    id: string;
    activity_id: string;
    activity_type: string;
    activity_title: string;
    content: string | null;
    status: 'pending' | 'published' | 'failed' | 'editing';
    image_url: string | null;
    error?: string;
}

interface PostQueuePanelProps {
    posts: Post[];
    onEdit: (postId: string, newContent: string) => void;
    onPublish: (postId: string) => void;
    onDiscard: (postId: string) => void;
    onSelectImage: (postId: string) => void;
    isPublishing: string | null;
    testMode: boolean;
}

export function PostQueuePanel({
    posts,
    onEdit,
    onPublish,
    onDiscard,
    onSelectImage,
    isPublishing,
    testMode
}: PostQueuePanelProps) {
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editContent, setEditContent] = useState('');
    const [expandedId, setExpandedId] = useState<string | null>(null);

    const handleStartEdit = (post: Post) => {
        setEditingId(post.id);
        setEditContent(post.content || '');
    };

    const handleSaveEdit = (postId: string) => {
        onEdit(postId, editContent);
        setEditingId(null);
        setEditContent('');
    };

    const handleCancelEdit = () => {
        setEditingId(null);
        setEditContent('');
    };

    const getStatusBadge = (status: string) => {
        const styles: Record<string, string> = {
            pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
            published: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
            failed: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
            editing: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
        };
        return styles[status] || styles.pending;
    };

    const getTypeIcon = (type: string) => {
        const icons: Record<string, string> = {
            push: '🚀',
            pull_request: '🔀',
            new_repo: '✨',
            issue: '🐛',
            release: '🎉'
        };
        return icons[type] || '📦';
    };

    if (posts.length === 0) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-xl p-8 text-center border border-gray-200 dark:border-gray-700">
                <div className="text-4xl mb-4">📭</div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    No posts in queue
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                    Scan your GitHub activity to generate posts
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Post Queue ({posts.length})
                </h3>
                {testMode && (
                    <span className="px-3 py-1 bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400 rounded-full text-sm font-medium">
                        🧪 Test Mode
                    </span>
                )}
            </div>

            <div className="space-y-4">
                {posts.map((post) => (
                    <div
                        key={post.id}
                        className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden transition-all duration-200 hover:shadow-lg"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl">{getTypeIcon(post.activity_type)}</span>
                                <div>
                                    <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                                        {post.activity_title || `${post.activity_type} activity`}
                                    </h4>
                                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(post.status)}`}>
                                        {post.status}
                                    </span>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                {post.image_url && (
                                    <span className="text-green-500" title="Image attached">🖼️</span>
                                )}
                                <button
                                    onClick={() => setExpandedId(expandedId === post.id ? null : post.id)}
                                    className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                                >
                                    {expandedId === post.id ? '▼' : '▶'}
                                </button>
                            </div>
                        </div>

                        {/* Content */}
                        {(expandedId === post.id || posts.length <= 3) && (
                            <div className="p-4">
                                {editingId === post.id ? (
                                    <div className="space-y-3">
                                        <textarea
                                            value={editContent}
                                            onChange={(e) => setEditContent(e.target.value)}
                                            className="w-full h-48 p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        />
                                        <div className="flex items-center justify-between">
                                            <CompactCharCounter text={editContent} />
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={() => handleSaveEdit(post.id)}
                                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                                                >
                                                    Save
                                                </button>
                                                <button
                                                    onClick={handleCancelEdit}
                                                    className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                                                >
                                                    Cancel
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <>
                                        {post.content ? (
                                            <div className="prose dark:prose-invert max-w-none">
                                                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap text-sm leading-relaxed">
                                                    {post.content}
                                                </p>
                                            </div>
                                        ) : (
                                            <p className="text-red-500">
                                                Failed to generate: {post.error || 'Unknown error'}
                                            </p>
                                        )}

                                        {/* Image preview */}
                                        {post.image_url && (
                                            <div className="mt-4">
                                                <img
                                                    src={post.image_url}
                                                    alt="Post image"
                                                    className="w-full h-40 object-cover rounded-lg"
                                                />
                                            </div>
                                        )}
                                    </>
                                )}
                            </div>
                        )}

                        {/* Actions */}
                        {post.content && editingId !== post.id && (
                            <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-700">
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => handleStartEdit(post)}
                                        className="px-3 py-1.5 text-sm bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                                    >
                                        ✏️ Edit
                                    </button>
                                    <button
                                        onClick={() => onSelectImage(post.id)}
                                        className="px-3 py-1.5 text-sm bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                                    >
                                        🖼️ {post.image_url ? 'Change' : 'Add'} Image
                                    </button>
                                    <button
                                        onClick={() => onDiscard(post.id)}
                                        className="px-3 py-1.5 text-sm bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
                                    >
                                        🗑️ Discard
                                    </button>
                                </div>
                                <button
                                    onClick={() => onPublish(post.id)}
                                    disabled={isPublishing === post.id || post.status === 'published'}
                                    className={`px-4 py-1.5 text-sm rounded-lg font-medium transition-colors ${post.status === 'published'
                                        ? 'bg-green-100 text-green-700 cursor-not-allowed'
                                        : isPublishing === post.id
                                            ? 'bg-blue-400 text-white cursor-wait'
                                            : testMode
                                                ? 'bg-orange-500 hover:bg-orange-600 text-white'
                                                : 'bg-blue-600 hover:bg-blue-700 text-white'
                                        }`}
                                >
                                    {isPublishing === post.id
                                        ? '⏳ Publishing...'
                                        : post.status === 'published'
                                            ? '✅ Published'
                                            : testMode
                                                ? '🧪 Test Publish'
                                                : '🚀 Publish'}
                                </button>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default PostQueuePanel;
