// Accessibility utilities for keyboard navigation and screen reader support

// Screen reader announcement utility
export const announceToScreenReader = (message: string, priority: 'polite' | 'assertive' = 'polite'): void => {
  const announcer = document.getElementById('sr-announcements') || document.getElementById('game-announcements');
  if (announcer) {
    announcer.setAttribute('aria-live', priority);
    announcer.textContent = message;
    
    // Clear after announcement to allow repeated messages
    setTimeout(() => {
      announcer.textContent = '';
    }, 100);
  }
};

// Keyboard navigation handler
export class KeyboardNavigationManager {
  private focusableElements: HTMLElement[] = [];
  private currentFocusIndex: number = -1;
  private container: HTMLElement | null = null;

  constructor(containerSelector?: string) {
    if (containerSelector) {
      this.container = document.querySelector(containerSelector);
    } else {
      this.container = document.body;
    }
    this.updateFocusableElements();
  }

  updateFocusableElements(): void {
    if (!this.container) return;

    const focusableSelector = [
      'button:not([disabled])',
      'input:not([disabled])',
      'textarea:not([disabled])',
      'select:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
      '[role="button"]:not([disabled])',
    ].join(', ');

    this.focusableElements = Array.from(
      this.container.querySelectorAll(focusableSelector)
    ) as HTMLElement[];
  }

  handleKeyNavigation(event: KeyboardEvent): boolean {
    switch (event.key) {
      case 'Tab':
        this.handleTabNavigation(event);
        return true;
      case 'ArrowUp':
      case 'ArrowDown':
        if (event.target && (event.target as HTMLElement).tagName !== 'TEXTAREA') {
          event.preventDefault();
          this.handleArrowNavigation(event.key === 'ArrowUp' ? -1 : 1);
          return true;
        }
        break;
      case 'Home':
        event.preventDefault();
        this.focusFirst();
        return true;
      case 'End':
        event.preventDefault();
        this.focusLast();
        return true;
      case 'Escape':
        this.handleEscape();
        return true;
    }
    return false;
  }

  private handleTabNavigation(event: KeyboardEvent): void {
    this.updateFocusableElements();
    
    if (this.focusableElements.length === 0) return;

    const currentElement = document.activeElement as HTMLElement;
    const currentIndex = this.focusableElements.indexOf(currentElement);

    if (event.shiftKey) {
      // Shift+Tab - move backwards
      const newIndex = currentIndex <= 0 ? this.focusableElements.length - 1 : currentIndex - 1;
      this.focusElementAt(newIndex);
    } else {
      // Tab - move forwards
      const newIndex = currentIndex >= this.focusableElements.length - 1 ? 0 : currentIndex + 1;
      this.focusElementAt(newIndex);
    }
  }

  private handleArrowNavigation(direction: number): void {
    this.updateFocusableElements();
    
    if (this.focusableElements.length === 0) return;

    const currentElement = document.activeElement as HTMLElement;
    let currentIndex = this.focusableElements.indexOf(currentElement);

    if (currentIndex === -1) {
      currentIndex = 0;
    } else {
      currentIndex += direction;
      if (currentIndex < 0) currentIndex = this.focusableElements.length - 1;
      if (currentIndex >= this.focusableElements.length) currentIndex = 0;
    }

    this.focusElementAt(currentIndex);
  }

  private focusElementAt(index: number): void {
    if (index >= 0 && index < this.focusableElements.length) {
      this.focusableElements[index].focus();
      this.currentFocusIndex = index;
    }
  }

  focusFirst(): void {
    this.updateFocusableElements();
    this.focusElementAt(0);
  }

  focusLast(): void {
    this.updateFocusableElements();
    this.focusElementAt(this.focusableElements.length - 1);
  }

  private handleEscape(): void {
    // Custom escape handling - could close modals, return to main menu, etc.
    const currentElement = document.activeElement as HTMLElement;
    if (currentElement && currentElement.blur) {
      currentElement.blur();
    }
  }
}

// Focus trap for modals and dialogs
export class FocusTrap {
  private container: HTMLElement;
  private firstFocusableElement: HTMLElement | null = null;
  private lastFocusableElement: HTMLElement | null = null;
  private previousActiveElement: HTMLElement | null = null;

  constructor(container: HTMLElement) {
    this.container = container;
    this.updateFocusableElements();
  }

  activate(): void {
    this.previousActiveElement = document.activeElement as HTMLElement;
    this.updateFocusableElements();
    
    if (this.firstFocusableElement) {
      this.firstFocusableElement.focus();
    }

    document.addEventListener('keydown', this.handleKeyDown);
  }

  deactivate(): void {
    document.removeEventListener('keydown', this.handleKeyDown);
    
    if (this.previousActiveElement) {
      this.previousActiveElement.focus();
    }
  }

  private updateFocusableElements(): void {
    const focusableSelector = [
      'button:not([disabled])',
      'input:not([disabled])',
      'textarea:not([disabled])',
      'select:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
    ].join(', ');

    const focusableElements = this.container.querySelectorAll(focusableSelector) as NodeListOf<HTMLElement>;
    this.firstFocusableElement = focusableElements[0] || null;
    this.lastFocusableElement = focusableElements[focusableElements.length - 1] || null;
  }

  private handleKeyDown = (event: KeyboardEvent): void => {
    if (event.key !== 'Tab') return;

    if (event.shiftKey) {
      if (document.activeElement === this.firstFocusableElement) {
        event.preventDefault();
        this.lastFocusableElement?.focus();
      }
    } else {
      if (document.activeElement === this.lastFocusableElement) {
        event.preventDefault();
        this.firstFocusableElement?.focus();
      }
    }
  };
}

// High contrast and reduced motion detection
export const getAccessibilityPreferences = () => {
  return {
    prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    prefersHighContrast: window.matchMedia('(prefers-contrast: high)').matches,
    prefersColorScheme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
  };
};

// Add accessibility attributes to an element
export const addAccessibilityAttributes = (
  element: HTMLElement,
  options: {
    role?: string;
    ariaLabel?: string;
    ariaDescribedBy?: string;
    ariaLive?: 'polite' | 'assertive' | 'off';
    ariaExpanded?: boolean;
    ariaPressed?: boolean;
    tabIndex?: number;
  }
): void => {
  const { role, ariaLabel, ariaDescribedBy, ariaLive, ariaExpanded, ariaPressed, tabIndex } = options;

  if (role) element.setAttribute('role', role);
  if (ariaLabel) element.setAttribute('aria-label', ariaLabel);
  if (ariaDescribedBy) element.setAttribute('aria-describedby', ariaDescribedBy);
  if (ariaLive) element.setAttribute('aria-live', ariaLive);
  if (ariaExpanded !== undefined) element.setAttribute('aria-expanded', ariaExpanded.toString());
  if (ariaPressed !== undefined) element.setAttribute('aria-pressed', ariaPressed.toString());
  if (tabIndex !== undefined) element.setAttribute('tabindex', tabIndex.toString());
};

// Create skip link for keyboard navigation
export const createSkipLink = (targetId: string, text: string = 'Skip to main content'): HTMLElement => {
  const skipLink = document.createElement('a');
  skipLink.href = `#${targetId}`;
  skipLink.textContent = text;
  skipLink.className = 'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-black focus:border focus:border-black';
  
  return skipLink;
};

// Debounced resize observer for responsive accessibility
export const createResponsiveAccessibilityObserver = (
  callback: (entries: ResizeObserverEntry[]) => void,
  debounceMs: number = 250
): ResizeObserver => {
  let timeoutId: number;

  return new ResizeObserver((entries) => {
    clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => callback(entries), debounceMs);
  });
};
