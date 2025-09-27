import React, { Component, ErrorInfo, ReactNode } from 'react';
import { announceToScreenReader } from '../utils/accessibility';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Game Error Boundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // Announce error to screen readers
    announceToScreenReader(
      'An error occurred in the game. Please try refreshing the page or starting a new game.',
      'assertive'
    );
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  handleRefresh = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div 
          className="min-h-screen bg-retro-black text-retro-green flex items-center justify-center p-4"
          role="alert"
          aria-labelledby="error-title"
          aria-describedby="error-description"
        >
          <div className="max-w-md w-full bg-retro-black border border-retro-green p-6 rounded font-mono">
            <div className="text-center mb-6">
              <h1 
                id="error-title" 
                className="text-2xl mb-4 text-retro-amber"
              >
                SYSTEM ERROR
              </h1>
              <div className="text-retro-green mb-4">
                ┌─────────────────────────┐<br/>
                │    ⚠️  ERROR DETECTED   │<br/>
                └─────────────────────────┘
              </div>
            </div>
            
            <div id="error-description" className="mb-6">
              <p className="mb-4 text-sm">
                Oops! Something went wrong with DyslexiQuest. 
                Don't worry - your progress is saved!
              </p>
              
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="mb-4 text-xs">
                  <summary className="cursor-pointer text-retro-amber hover:text-retro-green">
                    Technical Details (for developers)
                  </summary>
                  <pre className="mt-2 p-2 bg-black text-retro-green overflow-auto text-xs">
                    {this.state.error.toString()}
                    {this.state.errorInfo?.componentStack}
                  </pre>
                </details>
              )}
            </div>

            <div className="space-y-3">
              <button
                onClick={this.handleRetry}
                className="w-full px-4 py-2 bg-retro-green text-retro-black hover:bg-retro-dark-green focus:outline-none focus:ring-2 focus:ring-retro-green focus:ring-offset-2 focus:ring-offset-retro-black font-medium transition-colors"
                aria-describedby="retry-help"
              >
                TRY AGAIN
              </button>
              
              <button
                onClick={this.handleRefresh}
                className="w-full px-4 py-2 border border-retro-green text-retro-green hover:bg-retro-green hover:text-retro-black focus:outline-none focus:ring-2 focus:ring-retro-green focus:ring-offset-2 focus:ring-offset-retro-black font-medium transition-colors"
                aria-describedby="refresh-help"
              >
                REFRESH PAGE
              </button>

              <button
                onClick={() => {
                  localStorage.clear();
                  window.location.reload();
                }}
                className="w-full px-4 py-2 border border-retro-amber text-retro-amber hover:bg-retro-amber hover:text-retro-black focus:outline-none focus:ring-2 focus:ring-retro-amber focus:ring-offset-2 focus:ring-offset-retro-black font-medium transition-colors text-sm"
                aria-describedby="reset-help"
              >
                RESET ALL DATA
              </button>
            </div>

            <div className="mt-6 text-xs text-retro-green space-y-1">
              <p id="retry-help" className="sr-only">
                Try to continue with the current game state
              </p>
              <p id="refresh-help" className="sr-only">
                Reload the page to start fresh while keeping saved progress
              </p>
              <p id="reset-help" className="sr-only">
                Clear all saved data and start completely over
              </p>
              
              <p className="text-center text-retro-amber">
                Need help? Try refreshing or starting a new game.
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
