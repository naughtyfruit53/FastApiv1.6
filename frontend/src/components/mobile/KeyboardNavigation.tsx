import React, { useState, useEffect, useRef, ReactNode } from 'react';
import { Box } from '@mui/material';

interface FocusableElement {
  id: string;
  element: HTMLElement;
  tabIndex: number;
  disabled?: boolean;
}

interface KeyboardNavigationProps {
  children: ReactNode;
  enabled?: boolean;
  wrapAround?: boolean;
  initialFocus?: string;
  onFocusChange?: (elementId: string) => void;
  className?: string;
}

export const KeyboardNavigation: React.FC<KeyboardNavigationProps> = ({
  children,
  enabled = true,
  wrapAround = true,
  initialFocus,
  onFocusChange,
  className,
}) => {
  const [currentFocusIndex, setCurrentFocusIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const focusableElementsRef = useRef<FocusableElement[]>([]);

  const updateFocusableElements = () => {
    if (!containerRef.current) return;

    const elements = Array.from(
      containerRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
    ) as HTMLElement[];

    focusableElementsRef.current = elements
      .filter(el => !el.hasAttribute('disabled') && el.offsetParent !== null)
      .map((el, index) => ({
        id: el.id || `focusable-${index}`,
        element: el,
        tabIndex: parseInt(el.getAttribute('tabindex') || '0'),
        disabled: el.hasAttribute('disabled'),
      }))
      .sort((a, b) => a.tabIndex - b.tabIndex);
  };

  const focusElement = (index: number) => {
    const elements = focusableElementsRef.current;
    if (index >= 0 && index < elements.length) {
      const element = elements[index];
      element.element.focus();
      setCurrentFocusIndex(index);
      onFocusChange?.(element.id);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!enabled) return;

    const elements = focusableElementsRef.current;
    if (elements.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        e.preventDefault();
        if (currentFocusIndex < elements.length - 1) {
          focusElement(currentFocusIndex + 1);
        } else if (wrapAround) {
          focusElement(0);
        }
        break;

      case 'ArrowUp':
      case 'ArrowLeft':
        e.preventDefault();
        if (currentFocusIndex > 0) {
          focusElement(currentFocusIndex - 1);
        } else if (wrapAround) {
          focusElement(elements.length - 1);
        }
        break;

      case 'Home':
        e.preventDefault();
        focusElement(0);
        break;

      case 'End':
        e.preventDefault();
        focusElement(elements.length - 1);
        break;

      case 'Enter':
      case ' ':
        if (currentFocusIndex >= 0) {
          const element = elements[currentFocusIndex];
          if (element.element.tagName === 'BUTTON' || element.element.getAttribute('role') === 'button') {
            e.preventDefault();
            element.element.click();
          }
        }
        break;
    }
  };

  useEffect(() => {
    updateFocusableElements();
    
    if (initialFocus && focusableElementsRef.current.length > 0) {
      const initialIndex = focusableElementsRef.current.findIndex(
        el => el.id === initialFocus
      );
      if (initialIndex >= 0) {
        focusElement(initialIndex);
      }
    }
  }, [children, initialFocus]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const observer = new MutationObserver(() => {
      updateFocusableElements();
    });

    observer.observe(container, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['disabled', 'tabindex'],
    });

    return () => observer.disconnect();
  }, []);

  return (
    <Box
      ref={containerRef}
      className={className}
      onKeyDown={handleKeyDown}
      tabIndex={-1}
      sx={{
        outline: 'none',
        '& *:focus': {
          outline: '2px solid',
          outlineColor: 'primary.main',
          outlineOffset: '2px',
        },
      }}
    >
      {children}
    </Box>
  );
};

/**
 * Hook for managing focus within a component
 */
export const useFocusManager = (elementIds: string[] = []) => {
  const [currentFocus, setCurrentFocus] = useState<string | null>(null);
  const [focusHistory, setFocusHistory] = useState<string[]>([]);

  const focusElement = (elementId: string) => {
    const element = document.getElementById(elementId);
    if (element) {
      element.focus();
      setCurrentFocus(elementId);
      setFocusHistory(prev => [...prev.filter(id => id !== elementId), elementId]);
    }
  };

  const focusNext = () => {
    if (!currentFocus || elementIds.length === 0) return;
    
    const currentIndex = elementIds.indexOf(currentFocus);
    const nextIndex = (currentIndex + 1) % elementIds.length;
    focusElement(elementIds[nextIndex]);
  };

  const focusPrevious = () => {
    if (!currentFocus || elementIds.length === 0) return;
    
    const currentIndex = elementIds.indexOf(currentFocus);
    const previousIndex = currentIndex === 0 ? elementIds.length - 1 : currentIndex - 1;
    focusElement(elementIds[previousIndex]);
  };

  const focusFirst = () => {
    if (elementIds.length > 0) {
      focusElement(elementIds[0]);
    }
  };

  const focusLast = () => {
    if (elementIds.length > 0) {
      focusElement(elementIds[elementIds.length - 1]);
    }
  };

  const restoreFocus = () => {
    if (focusHistory.length > 1) {
      const previousFocus = focusHistory[focusHistory.length - 2];
      focusElement(previousFocus);
    }
  };

  const trapFocus = (containerRef: React.RefObject<HTMLElement>) => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      const container = containerRef.current;
      if (!container) return;

      const focusableElements = container.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      ) as NodeListOf<HTMLElement>;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  };

  return {
    currentFocus,
    focusHistory,
    focusElement,
    focusNext,
    focusPrevious,
    focusFirst,
    focusLast,
    restoreFocus,
    trapFocus,
  };
};

/**
 * Component for creating accessible skip links
 */
interface SkipLinkProps {
  href: string;
  children: ReactNode;
  className?: string;
}

export const SkipLink: React.FC<SkipLinkProps> = ({ href, children, className }) => {
  return (
    <Box
      component="a"
      href={href}
      className={className}
      sx={{
        position: 'absolute',
        left: '-9999px',
        zIndex: 9999,
        padding: 1,
        backgroundColor: 'primary.main',
        color: 'primary.contrastText',
        textDecoration: 'none',
        borderRadius: 1,
        '&:focus': {
          left: '10px',
          top: '10px',
        },
      }}
    >
      {children}
    </Box>
  );
};

export default KeyboardNavigation;