import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { handleLinkedInCallback } from '@/lib/api';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AuthCallback() {
  const router = useRouter();
  const [status, setStatus] = useState('Processing...');

  useEffect(() => {
    const processCallback = async () => {
      const { code, state, error } = router.query;
      
      // Handle error from LinkedIn
      if (error) {
        setStatus(`Error: ${error}`);
        setTimeout(() => {
          router.push(`/settings?linkedin_success=false&error=${encodeURIComponent(error as string)}`);
        }, 2000);
        return;
      }

      // Check if we have the authorization code
      if (!code || typeof code !== 'string') {
        return; // Still loading
      }

      try {
        setStatus('Exchanging authorization code...');

        // Build redirect URI
        const redirectUri = `${window.location.origin}/auth/callback`;

        // Exchange code for token via our backend
        const response = await fetch(
          `${API_BASE}/auth/linkedin/callback?code=${code}&redirect_uri=${encodeURIComponent(redirectUri)}&state=${state || ''}`
        );

        const data = await response.json();

        if (data.status === 'success' && data.linkedin_user_urn) {
          setStatus('Success! LinkedIn connected. Redirecting...');
          // Redirect back to settings with success
          setTimeout(() => {
            router.push(`/settings?linkedin_success=true&linkedin_urn=${encodeURIComponent(data.linkedin_user_urn)}`);
          }, 1500);
        } else {
          // Redirect with error
          const errorMsg = data.error || 'Unknown error occurred';
          setStatus(`Error: ${errorMsg}`);
          setTimeout(() => {
            router.push(`/settings?linkedin_success=false&error=${encodeURIComponent(errorMsg)}`);
          }, 2000);
        }
      } catch (err: any) {
        console.error('OAuth callback error:', err);
        setStatus(`Error: ${err.message || 'Network error'}`);
        setTimeout(() => {
          router.push(`/settings?linkedin_success=false&error=${encodeURIComponent(err.message || 'Network error')}`);
        }, 2000);
      }
    };

    if (router.isReady) {
      processCallback();
    }
  }, [router.isReady, router.query]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white p-8 rounded-2xl shadow-xl border border-gray-100 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          LinkedIn Authentication
        </h1>
        <p className="text-gray-600">{status}</p>
      </div>
    </div>
  );
}
