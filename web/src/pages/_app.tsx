import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { Toaster } from 'react-hot-toast'
import { ThemeProvider } from '@/components/ThemeProvider'
import ErrorBoundary from '@/components/ErrorBoundary'
import SkipToContent from '@/components/SkipToContent'

import { ClerkProvider } from '@clerk/nextjs'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ClerkProvider {...pageProps}>
      <ThemeProvider>
        <ErrorBoundary>
          <SkipToContent />
          <Component {...pageProps} />
          <Toaster />
        </ErrorBoundary>
      </ThemeProvider>
    </ClerkProvider>
  )
}
