import React from 'react';

interface PostPreviewProps {
    preview: string;
}

export const PostPreview: React.FC<PostPreviewProps> = ({ preview }) => {
    return (
        <div className="bg-white dark:bg-white/5 rounded-2xl shadow-lg border border-gray-100 dark:border-white/10 p-8 h-full flex flex-col">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">Post Preview</h3>
                <div className="flex items-center space-x-2">
                    {preview && (
                        <button
                            onClick={() => {
                                navigator.clipboard.writeText(preview);
                                // toast is handled by parent or we could add local state, but simple is fine
                            }}
                            className="px-3 py-2 text-sm bg-gray-100 dark:bg-white/10 hover:bg-gray-200 dark:hover:bg-white/20 text-gray-700 dark:text-gray-200 rounded-lg transition-all flex items-center"
                            title="Copy to clipboard"
                        >
                            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                            Copy
                        </button>
                    )}
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg shadow-purple-500/20">
                        <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                    </div>
                </div>
            </div>

            <div className="border-2 border-gray-200 dark:border-white/10 rounded-xl p-6 flex-1 bg-gradient-to-br from-gray-50 to-white dark:from-slate-900 dark:to-slate-800 relative overflow-hidden min-h-[400px]">
                {preview ? (
                    <div className="relative z-10 flex flex-col h-full">
                        <div className="absolute -top-2 -left-2 w-16 h-16 bg-blue-500 rounded-full opacity-10 blur-xl"></div>
                        <div className="absolute -bottom-2 -right-2 w-16 h-16 bg-purple-500 rounded-full opacity-10 blur-xl"></div>
                        <div className="whitespace-pre-wrap text-gray-800 dark:text-gray-200 leading-relaxed font-normal flex-1">{preview}</div>

                        {/* LinkedIn Post Preview Frame */}
                        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-white/10">
                            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                                <svg className="w-5 h-5 mr-2 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                                </svg>
                                Preview on LinkedIn
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-center">
                        <div className="w-20 h-20 bg-gradient-to-br from-gray-200 to-gray-300 dark:from-white/10 dark:to-white/5 rounded-2xl flex items-center justify-center mb-4">
                            <svg className="w-10 h-10 text-gray-400 dark:text-white/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <p className="text-gray-400 dark:text-gray-500 italic text-lg mb-2">No preview yet</p>
                        <p className="text-gray-500 dark:text-gray-600 text-sm max-w-xs">Click a GitHub activity or configure your context and click "Generate Preview"</p>
                    </div>
                )}
            </div>

            {/* Tips Section */}
            <div className="mt-6 bg-blue-50 dark:bg-blue-900/10 border-l-4 border-blue-600 rounded-r-lg p-4">
                <div className="flex items-start">
                    <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="flex-1">
                        <p className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Quick Tips</p>
                        <ul className="space-y-1 text-sm text-blue-800 dark:text-blue-200">
                            <li className="flex items-start">
                                <span className="text-blue-600 mr-2">•</span>
                                <span>Click any GitHub activity to auto-populate context</span>
                            </li>
                            <li className="flex items-start">
                                <span className="text-blue-600 mr-2">•</span>
                                <span>Use templates for quick post ideas</span>
                            </li>
                            <li className="flex items-start">
                                <span className="text-blue-600 mr-2">•</span>
                                <span>Test mode shows preview without posting to LinkedIn</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
};
