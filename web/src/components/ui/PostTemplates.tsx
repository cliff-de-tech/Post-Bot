import { useState, useEffect } from 'react';
import { showToast } from '@/lib/toast';

interface PostTemplate {
    id: string;
    name: string;
    icon: string;
    content: string;
    category: string;
    createdAt: number;
}

const STORAGE_KEY = 'linkedin_post_templates';

// Default templates
const DEFAULT_TEMPLATES: PostTemplate[] = [
    {
        id: 'default_1',
        name: 'Code Release',
        icon: '🚀',
        category: 'Technical',
        content: `Excited to announce the release of [PROJECT NAME] v[VERSION]!

Key highlights:
✨ [Feature 1]
⚡ [Feature 2]  
🔧 [Feature 3]

Check it out: [LINK]

#opensource #developers #coding`,
        createdAt: Date.now()
    },
    {
        id: 'default_2',
        name: 'Learning Journey',
        icon: '📚',
        category: 'Personal',
        content: `Today I learned about [TOPIC] and here's what stood out:

1️⃣ [Key insight]
2️⃣ [Practical application]
3️⃣ [Resource recommendation]

What's your experience with this? 👇

#learning #growth #techcommunity`,
        createdAt: Date.now()
    },
    {
        id: 'default_3',
        name: 'Project Update',
        icon: '🔨',
        category: 'Technical',
        content: `Progress update on [PROJECT]:

This week I:
✅ [Accomplishment 1]
✅ [Accomplishment 2]
🎯 Next up: [Next goal]

Building in public keeps me accountable!

#buildinpublic #indie #devlife`,
        createdAt: Date.now()
    }
];

export function usePostTemplates() {
    const [templates, setTemplates] = useState<PostTemplate[]>([]);

    // Load templates from localStorage
    useEffect(() => {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                const parsed = JSON.parse(saved);
                setTemplates([...DEFAULT_TEMPLATES, ...parsed]);
            } else {
                setTemplates(DEFAULT_TEMPLATES);
            }
        } catch {
            setTemplates(DEFAULT_TEMPLATES);
        }
    }, []);

    // Save custom templates
    const saveTemplate = (template: Omit<PostTemplate, 'id' | 'createdAt'>) => {
        const newTemplate: PostTemplate = {
            ...template,
            id: `custom_${Date.now()}`,
            createdAt: Date.now()
        };

        const userTemplates = templates.filter(t => t.id.startsWith('custom_'));
        const updatedUserTemplates = [...userTemplates, newTemplate];

        localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedUserTemplates));
        setTemplates([...DEFAULT_TEMPLATES, ...updatedUserTemplates]);
        showToast.success('Template saved!');

        return newTemplate;
    };

    // Delete custom template
    const deleteTemplate = (id: string) => {
        if (id.startsWith('default_')) {
            showToast.error('Cannot delete default templates');
            return;
        }

        const updated = templates.filter(t => t.id !== id);
        const userTemplates = updated.filter(t => t.id.startsWith('custom_'));

        localStorage.setItem(STORAGE_KEY, JSON.stringify(userTemplates));
        setTemplates(updated);
        showToast.success('Template deleted');
    };

    return { templates, saveTemplate, deleteTemplate };
}

// Template selector component
interface TemplateSelectorProps {
    onSelect: (content: string) => void;
    className?: string;
}

export function TemplateSelector({ onSelect, className = '' }: TemplateSelectorProps) {
    const { templates, deleteTemplate } = usePostTemplates();
    const [isOpen, setIsOpen] = useState(false);
    const [selectedCategory, setSelectedCategory] = useState<string>('all');

    const categories = ['all', ...new Set(templates.map(t => t.category))];
    const filteredTemplates = selectedCategory === 'all'
        ? templates
        : templates.filter(t => t.category === selectedCategory);

    return (
        <div className={`relative ${className}`}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="px-3 py-2 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded-lg text-sm font-medium hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors flex items-center gap-2"
            >
                <span>📝</span>
                Templates
                <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {isOpen && (
                <div className="absolute top-full left-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 z-50 scale-in">
                    {/* Category tabs */}
                    <div className="flex gap-1 p-2 border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
                        {categories.map(cat => (
                            <button
                                key={cat}
                                onClick={() => setSelectedCategory(cat)}
                                className={`px-3 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${selectedCategory === cat
                                        ? 'bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-400'
                                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                                    }`}
                            >
                                {cat.charAt(0).toUpperCase() + cat.slice(1)}
                            </button>
                        ))}
                    </div>

                    {/* Template list */}
                    <div className="max-h-64 overflow-y-auto p-2">
                        {filteredTemplates.map(template => (
                            <div
                                key={template.id}
                                className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer group transition-colors"
                                onClick={() => {
                                    onSelect(template.content);
                                    setIsOpen(false);
                                    showToast.success(`Applied "${template.name}" template`);
                                }}
                            >
                                <span className="text-2xl">{template.icon}</span>
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium text-gray-900 dark:text-white text-sm">{template.name}</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{template.content.substring(0, 50)}...</p>
                                </div>
                                {template.id.startsWith('custom_') && (
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            deleteTemplate(template.id);
                                        }}
                                        className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30 rounded transition-all"
                                    >
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
