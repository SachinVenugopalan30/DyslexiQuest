// Enhanced tooltip positioning utility
export const setupTooltipPositioning = () => {
  const handleTooltipPosition = () => {
    const tooltips = document.querySelectorAll('.vocabulary-tooltip');
    
    tooltips.forEach((tooltip) => {
      const word = tooltip.parentElement;
      if (!word) return;

      // Reset positioning
      tooltip.style.left = '50%';
      tooltip.style.transform = 'translateX(-50%)';
      tooltip.style.right = 'auto';

      // Get bounding rectangles
      const wordRect = word.getBoundingClientRect();
      const tooltipRect = tooltip.getBoundingClientRect();
      const container = word.closest('.retro-terminal');
      const containerRect = container?.getBoundingClientRect();

      if (!containerRect) return;

      // Calculate if tooltip would overflow
      const tooltipLeft = wordRect.left + wordRect.width / 2 - tooltipRect.width / 2;
      const tooltipRight = tooltipLeft + tooltipRect.width;

      // Adjust positioning if tooltip would overflow
      if (tooltipRight > containerRect.right - 10) {
        // Position tooltip to the right edge of container
        tooltip.style.left = 'auto';
        tooltip.style.right = '10px';
        tooltip.style.transform = 'none';
      } else if (tooltipLeft < containerRect.left + 10) {
        // Position tooltip to the left edge of container
        tooltip.style.left = '10px';
        tooltip.style.transform = 'none';
      }
    });
  };

  // Add event listeners for hover
  document.addEventListener('mouseover', (e) => {
    if (e.target?.classList.contains('vocabulary-word')) {
      setTimeout(handleTooltipPosition, 10);
    }
  });

  // Also handle window resize
  window.addEventListener('resize', handleTooltipPosition);
};

// Alternative: CSS-only solution using modern CSS anchor positioning
export const addModernTooltipStyles = () => {
  const style = document.createElement('style');
  style.textContent = `
    /* Modern anchor positioning for supported browsers */
    @supports (anchor-name: --vocab-anchor) {
      .vocabulary-word {
        anchor-name: --vocab-anchor;
      }
      
      .vocabulary-tooltip {
        position: absolute;
        position-anchor: --vocab-anchor;
        top: anchor(--vocab-anchor top);
        left: anchor(--vocab-anchor center);
        transform: translateX(-50%) translateY(calc(-100% - 12px));
        position-try-options: 
          flip-block flip-inline,
          flip-block,
          flip-inline;
      }
    }
    
    /* Fallback for browsers without anchor positioning */
    @supports not (anchor-name: --vocab-anchor) {
      .vocabulary-tooltip {
        /* Enhanced positioning with container queries */
        container-type: inline-size;
      }
      
      @container (max-width: 300px) {
        .vocabulary-tooltip {
          left: 10px;
          transform: none;
        }
      }
    }
  `;
  
  document.head.appendChild(style);
};
