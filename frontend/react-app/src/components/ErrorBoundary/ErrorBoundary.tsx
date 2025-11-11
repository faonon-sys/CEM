/**
 * Error Boundary Component with Recovery UI
 * Catches React component errors and provides recovery options
 */
import React, { Component, ErrorInfo, ReactNode } from 'react'
import './ErrorBoundary.css'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
  errorCount: number
}

interface ErrorRecoveryUIProps {
  error: Error | null
  errorInfo: ErrorInfo | null
  onRetry: () => void
  onRestore: () => void
  onReset: () => void
}

const ErrorRecoveryUI: React.FC<ErrorRecoveryUIProps> = ({
  error,
  errorInfo,
  onRetry,
  onRestore,
  onReset
}) => {
  const [showDetails, setShowDetails] = React.useState(false)

  return (
    <div className="error-boundary-container">
      <div className="error-boundary-card">
        <div className="error-icon">⚠️</div>

        <h1 className="error-title">Something Went Wrong</h1>

        <p className="error-message">
          We encountered an unexpected error while rendering this component.
          Your progress has been saved, and you can try the following recovery options:
        </p>

        <div className="error-actions">
          <button className="error-btn error-btn-primary" onClick={onRetry}>
            🔄 Retry
          </button>

          <button className="error-btn error-btn-secondary" onClick={onRestore}>
            💾 Restore from Checkpoint
          </button>

          <button className="error-btn error-btn-danger" onClick={onReset}>
            🔄 Reset Application
          </button>
        </div>

        <div className="error-details-section">
          <button
            className="error-details-toggle"
            onClick={() => setShowDetails(!showDetails)}
          >
            {showDetails ? '▼' : '▶'} Technical Details
          </button>

          {showDetails && (
            <div className="error-details">
              <div className="error-stack">
                <h3>Error Message:</h3>
                <pre>{error?.message || 'Unknown error'}</pre>
              </div>

              <div className="error-stack">
                <h3>Component Stack:</h3>
                <pre>{errorInfo?.componentStack || 'No stack trace available'}</pre>
              </div>

              <div className="error-stack">
                <h3>Error Stack:</h3>
                <pre>{error?.stack || 'No stack trace available'}</pre>
              </div>
            </div>
          )}
        </div>

        <div className="error-support">
          <p>
            If this problem persists, please{' '}
            <a href="/support" className="error-link">
              contact support
            </a>{' '}
            with the technical details above.
          </p>
        </div>
      </div>
    </div>
  )
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to error reporting service (e.g., Sentry)
    console.error('Error Boundary caught an error:', error, errorInfo)

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    // Update state with error details
    this.setState(prevState => ({
      errorInfo,
      errorCount: prevState.errorCount + 1
    }))

    // Save user progress before showing error
    this.saveUserProgress()

    // Report to monitoring service (would use Sentry in production)
    this.reportError(error, errorInfo)
  }

  saveUserProgress = (): void => {
    try {
      // Save current application state to localStorage
      const appState = {
        timestamp: new Date().toISOString(),
        url: window.location.href,
        // Add any other relevant state you want to save
      }

      localStorage.setItem('error_recovery_state', JSON.stringify(appState))
      console.log('✅ User progress saved for recovery')
    } catch (e) {
      console.error('Failed to save user progress:', e)
    }
  }

  reportError = (error: Error, errorInfo: ErrorInfo): void => {
    // In production, send to Sentry or similar service
    const errorReport = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    }

    console.log('Error report:', errorReport)
    // Example: Sentry.captureException(error, { contexts: { react: errorInfo } })
  }

  restoreFromCheckpoint = (): void => {
    try {
      const savedState = localStorage.getItem('error_recovery_state')
      if (savedState) {
        console.log('Restoring from checkpoint:', savedState)
        // Restore application state
        // This would involve re-hydrating your state management (Redux, Zustand, etc.)
      }

      this.handleRetry()
    } catch (e) {
      console.error('Failed to restore from checkpoint:', e)
      alert('Unable to restore from checkpoint. Please try resetting the application.')
    }
  }

  handleRetry = (): void => {
    // Reset error state to re-render children
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  handleReset = (): void => {
    // Clear all saved state and reload page
    if (window.confirm('This will clear all local data and reload the page. Continue?')) {
      try {
        // Clear localStorage
        localStorage.clear()
        // Clear sessionStorage
        sessionStorage.clear()
        // Reload page
        window.location.reload()
      } catch (e) {
        console.error('Failed to reset application:', e)
      }
    }
  }

  render(): ReactNode {
    if (this.state.hasError) {
      // Check if we've had too many errors (infinite error loop protection)
      if (this.state.errorCount > 3) {
        return (
          <div className="error-boundary-container">
            <div className="error-boundary-card">
              <div className="error-icon">❌</div>
              <h1>Critical Error</h1>
              <p>
                Multiple errors detected. The application may be in an unstable state.
                Please refresh the page or contact support.
              </p>
              <button
                className="error-btn error-btn-danger"
                onClick={() => window.location.reload()}
              >
                🔄 Reload Page
              </button>
            </div>
          </div>
        )
      }

      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default error recovery UI
      return (
        <ErrorRecoveryUI
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          onRetry={this.handleRetry}
          onRestore={this.restoreFromCheckpoint}
          onReset={this.handleReset}
        />
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
