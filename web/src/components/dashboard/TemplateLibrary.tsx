import React, { useState } from 'react';

interface Template {
    id: string;
    name: string;
    icon: string;
    description: string;
    category: 'tech' | 'career' | 'learning' | 'project' | 'engagement';
    prompt: string;
    example?: string;
}

interface TemplateLibraryProps {
    onSelect: (template: Template) => void;
    isOpen: boolean;
    onClose: () => void;
}

// Expanded template library with categories
const templates: Template[] = [
    // Tech Updates
    {
        id: 'feature-release',
        name: 'Feature Release',
        icon: '🚀',
        description: 'Announce a new feature or update',
        category: 'tech',
        prompt: 'Announce a new feature with excitement and technical details',
        example: '🚀 Just shipped a major update...',
    },
    {
        id: 'tech-insight',
        name: 'Tech Insight',
        icon: '💡',
        description: 'Share a technical insight or lesson',
        category: 'tech',
        prompt: 'Share a technical insight from recent work',
        example: '💡 Today I learned something fascinating about...',
    },
    {
        id: 'bug-fix',
        name: 'Bug Fix Story',
        icon: '🐛',
        description: 'Share a debugging adventure',
        category: 'tech',
        prompt: 'Tell a story about fixing a challenging bug',
        example: '🐛 Spent 4 hours debugging only to find...',
    },
    // Career
    {
        id: 'milestone',
        name: 'Career Milestone',
        icon: '🎉',
        description: 'Celebrate a career achievement',
        category: 'career',
        prompt: 'Celebrate a professional milestone or achievement',
        example: '🎉 Thrilled to announce...',
    },
    {
        id: 'job-search',
        name: 'Open to Work',
        icon: '🔍',
        description: 'Announce you\'re looking for opportunities',
        category: 'career',
        prompt: 'Professional open-to-work announcement',
        example: '🔍 After an amazing journey at...',
    },
    // Learning
    {
        id: 'learning-journey',
        name: 'Learning Journey',
        icon: '📚',
        description: 'Share what you\'re learning',
        category: 'learning',
        prompt: 'Share your learning journey and progress',
        example: '📚 Week 4 of learning...',
    },
    {
        id: 'book-recommendation',
        name: 'Book/Resource',
        icon: '📖',
        description: 'Recommend a helpful resource',
        category: 'learning',
        prompt: 'Recommend a book or learning resource',
        example: '📖 Just finished reading...',
    },
    // Project
    {
        id: 'side-project',
        name: 'Side Project',
        icon: '🛠️',
        description: 'Share a side project update',
        category: 'project',
        prompt: 'Share progress on a side project',
        example: '🛠️ Weekend project update...',
    },
    {
        id: 'open-source',
        name: 'Open Source',
        icon: '🌟',
        description: 'Contribute to open source',
        category: 'project',
        prompt: 'Share open source contribution',
        example: '🌟 Just merged my first PR to...',
    },
    // Engagement
    {
        id: 'question',
        name: 'Ask Community',
        icon: '❓',
        description: 'Ask your network a question',
        category: 'engagement',
        prompt: 'Ask an engaging question to your network',
        example: '❓ Curious to know...',
    },
    {
        id: 'poll',
        name: 'Thought Poll',
        icon: '📊',
        description: 'Start a discussion with choices',
        category: 'engagement',
        prompt: 'Create a thought-provoking poll topic',
        example: '📊 Hot take: Which do you prefer...',
    },
    {
        id: 'gratitude',
        name: 'Gratitude Post',
        icon: '🙏',
        description: 'Thank your community or mentors',
        category: 'engagement',
        prompt: 'Express gratitude to community or mentors',
        example: '🙏 Grateful for...',
    },
];

const categories = [
    { id: 'all', label: 'All', icon: '✨' },
    { id: 'tech', label: 'Tech', icon: '💻' },
    { id: 'career', label: 'Career', icon: '💼' },
    { id: 'learning', label: 'Learning', icon: '📚' },
    { id: 'project', label: 'Projects', icon: '🛠️' },
    { id: 'engagement', label: 'Engagement', icon: '💬' },
];

/**
 * Template Library component with categories and search
 */
const TemplateLibrary: React.FC<TemplateLibraryProps> = ({ onSelect, isOpen, onClose }) => {
    const [selectedCategory, setSelectedCategory] = useState<string>('all');
    const [searchQuery, setSearchQuery] = useState('');

    if (!isOpen) return null;

    const filteredTemplates = templates.filter((template) => {
        const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
        const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            template.description.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesCategory && matchesSearch;
    });

    return (
        <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={onClose}
            role="dialog"
            aria-modal="true"
            aria-labelledby="template-library-title"
        >
            <div
                className="bg-white dark:bg-gray-900 rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden shadow-2xl"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                                <span className="text-2xl">📝</span>
                            </div>
                            <div>
                                <h2 id="template-library-title" className="text-xl font-bold">Template Library</h2>
                                <p className="text-purple-100 text-sm">Choose a template to get started</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                            aria-label="Close template library"
                        >
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Search */}
                    <div className="relative">
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search templates..."
                            className="w-full px-4 py-3 pl-10 bg-white/10 border border-white/20 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30"
                            aria-label="Search templates"
                        />
                        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/60" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>
                </div>

                {/* Categories */}
                <div className="px-6 py-4 border-b border-gray-100 dark:border-white/10 flex gap-2 overflow-x-auto">
                    {categories.map((category) => (
                        <button
                            key={category.id}
                            onClick={() => setSelectedCategory(category.id)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${selectedCategory === category.id
                                    ? 'bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-300'
                                    : 'bg-gray-100 text-gray-600 dark:bg-white/5 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-white/10'
                                }`}
                        >
                            <span aria-hidden="true">{category.icon}</span>
                            {category.label}
                        </button>
                    ))}
                </div>

                {/* Templates Grid */}
                <div className="p-6 overflow-y-auto max-h-[50vh]">
                    {filteredTemplates.length === 0 ? (
                        <div className="text-center py-12">
                            <span className="text-4xl mb-3 block" aria-hidden="true">🔍</span>
                            <p className="text-gray-600 dark:text-gray-400">No templates found</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {filteredTemplates.map((template) => (
                                <button
                                    key={template.id}
                                    onClick={() => {
                                        onSelect(template);
                                        onClose();
                                    }}
                                    className="text-left p-4 bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl hover:border-purple-400 dark:hover:border-purple-500 hover:shadow-md transition-all group"
                                >
                                    <div className="flex items-start gap-3">
                                        <span className="text-2xl" aria-hidden="true">{template.icon}</span>
                                        <div className="flex-1 min-w-0">
                                            <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                                                {template.name}
                                            </h3>
                                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                                {template.description}
                                            </p>
                                            {template.example && (
                                                <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 italic">
                                                    "{template.example}"
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TemplateLibrary;
