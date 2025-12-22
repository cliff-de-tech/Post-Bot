/**
 * GitHub OAuth Callback Handler
 * 
 * Handles the callback from GitHub OAuth flow.
 * Exchanges code for token via backend and redirects to settings.
 */
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import { useUser } from '@clerk/nextjs';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function GitHubCallback() {
    const router = useRouter();
    const { user, isLoaded } = useUser();
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [message, setMessage] = useState('Connecting to GitHub...');

    useEffect(() => {
        if (!isLoaded) return;

        const handleCallback = async () => {
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code');
            const state = urlParams.get('state');
            const error = urlParams.get('error');

            if (error) {
                setStatus('error');
                setMessage(`GitHub authorization failed: ${error}`);
                setTimeout(() => {
                    router.push('/settings?github_success=false&error=' + encodeURIComponent(error));
                }, 2000);
                return;
            }

            if (!code) {
                setStatus('error');
                setMessage('No authorization code received');
                setTimeout(() => {
                    router.push('/settings?github_success=false&error=no_code');
                }, 2000);
                return;
            }

            try {
                // Exchange code for token via backend
                const redirectUri = `${window.location.origin}/auth/github/callback`;
                const response = await axios.get(
                    `${API_BASE}/auth/github/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state || '')}&redirect_uri=${encodeURIComponent(redirectUri)}`
                );

                if (response.data.status === 'success') {
                    setStatus('success');
                    setMessage('GitHub connected successfully!');
                    setTimeout(() => {
                        // Redirect back to settings or onboarding
                        const fromOnboarding = localStorage.getItem('github_oauth_from_onboarding');
                        if (fromOnboarding) {
                            localStorage.removeItem('github_oauth_from_onboarding');
                            router.push('/onboarding?github_success=true');
                        } else {
                            router.push('/settings?github_success=true');
                        }
                    }, 1500);
                } else {
                    throw new Error(response.data.error || 'Unknown error');
                }
            } catch (err: any) {
                setStatus('error');
                setMessage(err.response?.data?.error || err.message || 'Failed to connect GitHub');
                setTimeout(() => {
                    router.push('/settings?github_success=false&error=' + encodeURIComponent(err.message || 'unknown'));
                }, 2000);
            }
        };

        handleCallback();
    }, [isLoaded, router]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
            <div className="text-center p-8 bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-md">
                {status === 'loading' && (
                    <>
                        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-gray-900 dark:border-white mx-auto mb-4"></div>
                        <p className="text-gray-600 dark:text-gray-300">{message}</p>
                    </>
                )}
                {status === 'success' && (
                    <>
                        <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg className="w-10 h-10 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <p className="text-green-600 dark:text-green-400 font-medium">{message}</p>
                        <p className="text-gray-500 text-sm mt-2">Redirecting...</p>
                    </>
                )}
                {status === 'error' && (
                    <>
                        <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg className="w-10 h-10 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </div>
                        <p className="text-red-600 dark:text-red-400 font-medium">{message}</p>
                        <p className="text-gray-500 text-sm mt-2">Redirecting...</p>
                    </>
                )}
            </div>
        </div>
    );
}
