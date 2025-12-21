import { useState } from 'react';

interface Image {
    id: string;
    url: string;
    thumb: string;
    description: string;
    photographer: string;
    download_url: string;
}

interface ImageSelectorProps {
    images: Image[];
    selectedImage: string | null;
    onSelect: (imageUrl: string | null) => void;
    onClose: () => void;
    loading: boolean;
    onRefresh: () => void;
}

export function ImageSelector({
    images,
    selectedImage,
    onSelect,
    onClose,
    loading,
    onRefresh
}: ImageSelectorProps) {
    const [hoveredId, setHoveredId] = useState<string | null>(null);

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                    <div>
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                            Select an Image
                        </h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            Choose an image to accompany your post
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={onRefresh}
                            disabled={loading}
                            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                            title="Get new images"
                        >
                            {loading ? '⏳' : '🔄'}
                        </button>
                        <button
                            onClick={onClose}
                            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                        >
                            ✕
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[60vh]">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-12">
                            <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mb-4"></div>
                            <p className="text-gray-500 dark:text-gray-400">Loading images...</p>
                        </div>
                    ) : images.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="text-4xl mb-4">🖼️</div>
                            <p className="text-gray-500 dark:text-gray-400">No images available</p>
                            <button
                                onClick={onRefresh}
                                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                            >
                                Try Again
                            </button>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {images.map((image) => (
                                <div
                                    key={image.id}
                                    className={`relative rounded-xl overflow-hidden cursor-pointer transition-all duration-200 ${selectedImage === image.url
                                            ? 'ring-4 ring-blue-500 shadow-lg scale-[1.02]'
                                            : 'hover:shadow-lg hover:scale-[1.02]'
                                        }`}
                                    onClick={() => onSelect(selectedImage === image.url ? null : image.url)}
                                    onMouseEnter={() => setHoveredId(image.id)}
                                    onMouseLeave={() => setHoveredId(null)}
                                >
                                    <img
                                        src={image.thumb}
                                        alt={image.description}
                                        className="w-full h-48 object-cover"
                                    />

                                    {/* Overlay on hover or selected */}
                                    {(hoveredId === image.id || selectedImage === image.url) && (
                                        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent flex flex-col justify-end p-4">
                                            <p className="text-white text-sm font-medium truncate">
                                                {image.description || 'No description'}
                                            </p>
                                            <p className="text-gray-300 text-xs mt-1">
                                                📷 {image.photographer}
                                            </p>
                                        </div>
                                    )}

                                    {/* Selected indicator */}
                                    {selectedImage === image.url && (
                                        <div className="absolute top-3 right-3 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center shadow-lg">
                                            <span className="text-white text-lg">✓</span>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {/* No image option */}
                    <div
                        className={`mt-4 p-4 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-200 ${selectedImage === null
                                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                                : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                            }`}
                        onClick={() => onSelect(null)}
                    >
                        <div className="flex items-center justify-center gap-3">
                            <span className="text-2xl">🚫</span>
                            <div>
                                <p className="font-medium text-gray-900 dark:text-white">
                                    No Image
                                </p>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    Post without an image
                                </p>
                            </div>
                            {selectedImage === null && (
                                <span className="ml-auto text-blue-500 text-xl">✓</span>
                            )}
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                        Images from <span className="font-medium">Unsplash</span>
                    </p>
                    <div className="flex gap-3">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={onClose}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            Confirm Selection
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ImageSelector;
