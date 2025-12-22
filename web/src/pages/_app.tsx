import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { useRouter } from 'next/router'
import { Toaster } from 'react-hot-toast'
import { ThemeProvider } from '@/components/ThemeProvider'
import ErrorBoundary from '@/components/ErrorBoundary'
import SkipToContent from '@/components/SkipToContent'
import AnimatedBackground from '@/components/ui/AnimatedBackground'

import { ClerkProvider } from '@clerk/nextjs'

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const isOnboarding = router.pathname === '/onboarding';

  return (
    <ClerkProvider {...pageProps}>
      <ThemeProvider>
        <ErrorBoundary>
          {/* Global animated background - Interactive particle theme on all pages EXCEPT onboarding */}
          {!isOnboarding && (
            <AnimatedBackground intensity="subtle" variant="interactive" fixed={true} />
          )}
          <SkipToContent />
          <Component {...pageProps} />
          <Toaster />
        </ErrorBoundary>
      </ThemeProvider>
    </ClerkProvider>
  )
}
