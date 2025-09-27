// Utility for smart tooltip positioning to prevent overflow

export const setupTooltipPositioning = () => {
  // Add the global function to window for inline event handlers
  (window as any).positionTooltip = (element: HTMLElement) => {
    const tooltipId = element.getAttribute('data-tooltip-id');
    if (!tooltipId) return;

    const tooltip = document.getElementById(tooltipId);
    if (!tooltip) return;

    // Reset classes
    tooltip.classList.remove('tooltip-left', 'tooltip-right');

    // Get bounding rectangles
    const elementRect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    const viewportWidth = window.innerWidth;

    // Calculate positions
    const elementCenter = elementRect.left + elementRect.width / 2;
    const tooltipHalfWidth = tooltipRect.width / 2;

    // Check if tooltip would overflow on the right
    if (elementCenter + tooltipHalfWidth > viewportWidth - 20) {
      tooltip.classList.add('tooltip-right');
    }
    // Check if tooltip would overflow on the left
    else if (elementCenter - tooltipHalfWidth < 20) {
      tooltip.classList.add('tooltip-left');
    }
    // Default center positioning is fine
  };

  // Also setup intersection observer to handle tooltips that are partially visible
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.target.classList.contains('vocabulary-word')) {
        const element = entry.target as HTMLElement;
        const tooltipId = element.getAttribute('data-tooltip-id');
        if (tooltipId) {
          const tooltip = document.getElementById(tooltipId);
          if (tooltip && entry.intersectionRatio < 1) {
            // Element is partially out of view, adjust tooltip
            (window as any).positionTooltip(element);
          }
        }
      }
    });
  }, {
    threshold: [0.9, 1.0]
  });

  // Observe all vocabulary words
  const observeVocabularyWords = () => {
    document.querySelectorAll('.vocabulary-word').forEach((word) => {
      observer.observe(word);
    });
  };

  // Setup mutation observer to watch for new vocabulary words
  const mutationObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === Node.ELEMENT_NODE) {
          const element = node as Element;
          // Check if the added element contains vocabulary words
          const vocabWords = element.querySelectorAll?.('.vocabulary-word') || [];
          vocabWords.forEach((word) => {
            observer.observe(word);
          });
        }
      });
    });
  });

  // Start observing
  mutationObserver.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Initial observation
  observeVocabularyWords();
};

// Alternative approach: Use CSS-only solution with modern CSS
export const addSmartTooltipCSS = () => {
  const style = document.createElement('style');
  style.textContent = `
    .vocabulary-word {
      position: relative;
      display: inline-block;
    }

    .vocabulary-tooltip {
      position: absolute;
      bottom: 100%;
      left: 50%;
      transform: translateX(-50%);
      margin-bottom: 8px;
      background: #000000;
      border: 1px solid #00ff00;
      border-radius: 4px;
      padding: 8px 12px;
      font-size: 0.875rem;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s;
      z-index: 1000;
      white-space: nowrap;
      min-width: 200px;
      max-width: 300px;
      white-space: normal;
      
      /* Use container queries for smart positioning */
      container: tooltip-container / inline-size;
    }

    .vocabulary-word:hover .vocabulary-tooltip {
      opacity: 1;
      pointer-events: auto;
    }

    /* Prevent tooltip overflow using logical properties */
    @supports (anchor-name: --tooltip-anchor) {
      .vocabulary-word {
        anchor-name: --tooltip-anchor;
      }
      
      .vocabulary-tooltip {
        position: fixed;
        position-anchor: --tooltip-anchor;
        position-area: block-start span-inline-start;
        position-try-options: 
          block-end span-inline-start,
          block-start span-inline-end,
          block-end span-inline-end;
      }
    }
  `;
  
  document.head.appendChild(style);
};
