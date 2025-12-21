import React, { useEffect, useState, useRef } from 'react';

interface AnimatedCounterProps {
    end: number;
    duration?: number;
    suffix?: string;
    prefix?: string;
    className?: string;
}

/**
 * Animated counter that counts up to a target number
 */
export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
    end,
    duration = 2000,
    suffix = '',
    prefix = '',
    className = '',
}) => {
    const [count, setCount] = useState(0);
    const [isVisible, setIsVisible] = useState(false);
    const ref = useRef<HTMLSpanElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsVisible(true);
                }
            },
            { threshold: 0.1 }
        );

        if (ref.current) {
            observer.observe(ref.current);
        }

        return () => observer.disconnect();
    }, []);

    useEffect(() => {
        if (!isVisible) return;

        let startTime: number;
        const startValue = 0;

        const step = (timestamp: number) => {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);

            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            setCount(Math.floor(easeOutQuart * (end - startValue) + startValue));

            if (progress < 1) {
                requestAnimationFrame(step);
            }
        };

        requestAnimationFrame(step);
    }, [isVisible, end, duration]);

    return (
        <span ref={ref} className={className}>
            {prefix}{count.toLocaleString()}{suffix}
        </span>
    );
};

interface TypewriterProps {
    texts: string[];
    speed?: number;
    deleteSpeed?: number;
    pauseDuration?: number;
    className?: string;
}

/**
 * Typewriter effect that cycles through multiple texts
 */
export const Typewriter: React.FC<TypewriterProps> = ({
    texts,
    speed = 100,
    deleteSpeed = 50,
    pauseDuration = 2000,
    className = '',
}) => {
    const [displayText, setDisplayText] = useState('');
    const [textIndex, setTextIndex] = useState(0);
    const [isDeleting, setIsDeleting] = useState(false);
    const [isPaused, setIsPaused] = useState(false);

    useEffect(() => {
        const currentText = texts[textIndex];

        if (isPaused) {
            const pauseTimer = setTimeout(() => {
                setIsPaused(false);
                setIsDeleting(true);
            }, pauseDuration);
            return () => clearTimeout(pauseTimer);
        }

        if (isDeleting) {
            if (displayText === '') {
                setIsDeleting(false);
                setTextIndex((prev) => (prev + 1) % texts.length);
            } else {
                const timer = setTimeout(() => {
                    setDisplayText(displayText.slice(0, -1));
                }, deleteSpeed);
                return () => clearTimeout(timer);
            }
        } else {
            if (displayText === currentText) {
                setIsPaused(true);
            } else {
                const timer = setTimeout(() => {
                    setDisplayText(currentText.slice(0, displayText.length + 1));
                }, speed);
                return () => clearTimeout(timer);
            }
        }
    }, [displayText, textIndex, isDeleting, isPaused, texts, speed, deleteSpeed, pauseDuration]);

    return (
        <span className={className}>
            {displayText}
            <span className="animate-pulse">|</span>
        </span>
    );
};

interface ScrollProgressProps {
    color?: string;
}

/**
 * Scroll progress indicator bar
 */
export const ScrollProgress: React.FC<ScrollProgressProps> = ({
    color = 'bg-gradient-to-r from-blue-600 to-purple-600'
}) => {
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        const handleScroll = () => {
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            setProgress(scrollPercent);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <div className="fixed top-0 left-0 w-full h-1 z-[100]">
            <div
                className={`h-full ${color} transition-all duration-100`}
                style={{ width: `${progress}%` }}
            />
        </div>
    );
};

interface TrustBadgeProps {
    icon: React.ReactNode;
    title: string;
    subtitle?: string;
}

/**
 * Trust/security badge component
 */
export const TrustBadge: React.FC<TrustBadgeProps> = ({ icon, title, subtitle }) => (
    <div className="flex items-center gap-3 px-4 py-3 bg-white dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 shadow-sm">
        <div className="w-10 h-10 bg-green-100 dark:bg-green-500/20 rounded-lg flex items-center justify-center text-green-600 dark:text-green-400">
            {icon}
        </div>
        <div>
            <p className="font-semibold text-gray-900 dark:text-white text-sm">{title}</p>
            {subtitle && <p className="text-xs text-gray-500 dark:text-gray-400">{subtitle}</p>}
        </div>
    </div>
);

interface LogoCarouselProps {
    logos: { name: string; initial: string; color: string }[];
}

/**
 * Animated logo carousel for social proof
 */
export const LogoCarousel: React.FC<LogoCarouselProps> = ({ logos }) => (
    <div className="overflow-hidden py-4">
        <div className="flex animate-scroll gap-8">
            {[...logos, ...logos].map((logo, idx) => (
                <div
                    key={idx}
                    className={`flex-shrink-0 w-16 h-16 ${logo.color} rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg`}
                >
                    {logo.initial}
                </div>
            ))}
        </div>
    </div>
);

interface FAQItem {
    question: string;
    answer: string;
}

interface FAQAccordionProps {
    items: FAQItem[];
}

/**
 * FAQ Accordion component
 */
export const FAQAccordion: React.FC<FAQAccordionProps> = ({ items }) => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    return (
        <div className="space-y-4">
            {items.map((item, index) => (
                <div
                    key={index}
                    className="bg-white dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/10 overflow-hidden"
                >
                    <button
                        onClick={() => setOpenIndex(openIndex === index ? null : index)}
                        className="w-full px-6 py-4 flex items-center justify-between text-left"
                        aria-expanded={openIndex === index}
                    >
                        <span className="font-semibold text-gray-900 dark:text-white">{item.question}</span>
                        <svg
                            className={`w-5 h-5 text-gray-500 transition-transform duration-300 ${openIndex === index ? 'rotate-180' : ''
                                }`}
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                    </button>
                    <div
                        className={`overflow-hidden transition-all duration-300 ${openIndex === index ? 'max-h-96' : 'max-h-0'
                            }`}
                    >
                        <p className="px-6 pb-4 text-gray-600 dark:text-gray-400">{item.answer}</p>
                    </div>
                </div>
            ))}
        </div>
    );
};

interface ComparisonTableProps {
    before: string[];
    after: string[];
}

/**
 * Before/After comparison table
 */
export const ComparisonTable: React.FC<ComparisonTableProps> = ({ before, after }) => (
    <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-red-50 dark:bg-red-500/10 rounded-2xl p-6 border border-red-100 dark:border-red-500/20">
            <h3 className="text-lg font-bold text-red-800 dark:text-red-300 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Without LinkedIn Post Bot
            </h3>
            <ul className="space-y-3">
                {before.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-red-700 dark:text-red-300">
                        <span className="mt-1">•</span>
                        <span>{item}</span>
                    </li>
                ))}
            </ul>
        </div>

        <div className="bg-green-50 dark:bg-green-500/10 rounded-2xl p-6 border border-green-100 dark:border-green-500/20">
            <h3 className="text-lg font-bold text-green-800 dark:text-green-300 mb-4 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                With LinkedIn Post Bot
            </h3>
            <ul className="space-y-3">
                {after.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-green-700 dark:text-green-300">
                        <span className="mt-1">✓</span>
                        <span>{item}</span>
                    </li>
                ))}
            </ul>
        </div>
    </div>
);

interface FeatureTabsProps {
    tabs: { id: string; label: string; icon: React.ReactNode; content: React.ReactNode }[];
}

/**
 * Interactive feature tabs component
 */
export const FeatureTabs: React.FC<FeatureTabsProps> = ({ tabs }) => {
    const [activeTab, setActiveTab] = useState(tabs[0]?.id || '');

    return (
        <div>
            <div className="flex flex-wrap gap-2 mb-6 justify-center">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${activeTab === tab.id
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 dark:bg-white/10 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-white/20'
                            }`}
                    >
                        {tab.icon}
                        {tab.label}
                    </button>
                ))}
            </div>
            <div className="bg-white dark:bg-white/5 rounded-2xl p-8 border border-gray-100 dark:border-white/10 shadow-lg animate-fade-in-up">
                {tabs.find((t) => t.id === activeTab)?.content}
            </div>
        </div>
    );
};
