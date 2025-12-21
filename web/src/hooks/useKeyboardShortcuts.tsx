import { useEffect } from 'react';

type KeyHandler = (e: KeyboardEvent) => void;

interface ShortcutConfig {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  handler: KeyHandler;
  description?: string;
}

// Global keyboard shortcuts hook
export function useKeyboardShortcuts(shortcuts: ShortcutConfig[], enabled = true) {
  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input/textarea
      const target = e.target as HTMLElement;
      const isTyping = ['INPUT', 'TEXTAREA'].includes(target.tagName) || target.isContentEditable;

      for (const shortcut of shortcuts) {
        const keyMatch = e.key.toLowerCase() === shortcut.key.toLowerCase();
        const ctrlMatch = shortcut.ctrl ? (e.ctrlKey || e.metaKey) : true;
        const shiftMatch = shortcut.shift ? e.shiftKey : !e.shiftKey;
        const altMatch = shortcut.alt ? e.altKey : !e.altKey;

        // For shortcuts that should work even while typing (like Ctrl+Enter)
        const requiresModifier = shortcut.ctrl || shortcut.alt;

        if (keyMatch && ctrlMatch && shiftMatch && altMatch && (requiresModifier || !isTyping)) {
          e.preventDefault();
          shortcut.handler(e);
          return;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts, enabled]);
}

// Common shortcut patterns
export function usePublishShortcut(onPublish: () => void, enabled = true) {
  const shortcuts: ShortcutConfig[] = [
    { key: 'Enter', ctrl: true, handler: onPublish, description: 'Publish post (Ctrl+Enter)' }
  ];
  useKeyboardShortcuts(shortcuts, enabled);
}

export function useEscapeShortcut(onEscape: () => void, enabled = true) {
  const shortcuts: ShortcutConfig[] = [
    { key: 'Escape', handler: onEscape, description: 'Close/Cancel (Esc)' }
  ];
  useKeyboardShortcuts(shortcuts, enabled);
}

// Shortcut hint component
export function ShortcutHint({ keys, className = '' }: { keys: string[]; className?: string }) {
  return (
    <span className={`inline-flex items-center gap-0.5 ${className}`}>
      {keys.map((key, i) => (
        <span key={i}>
          <kbd className="px-1.5 py-0.5 text-xs font-mono bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-gray-600 dark:text-gray-300">
            {key}
          </kbd>
          {i < keys.length - 1 && <span className="mx-0.5 text-gray-400">+</span>}
        </span>
      ))}
    </span>
  );
}
