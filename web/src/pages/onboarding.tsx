import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';
import { useUser } from '@clerk/nextjs';
import { showToast } from '@/lib/toast';
import SEOHead from '@/components/SEOHead';
import ThemeToggle from '@/components/ThemeToggle';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Onboarding() {
  const router = useRouter();
  const { user, isLoaded, isSignedIn } = useUser();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const userId = user?.id;

  // Form State
  const [formData, setFormData] = useState({
    linkedin_client_id: '',
    linkedin_client_secret: '',
    groq_api_key: '',
    github_username: '',
    unsplash_access_key: ''
  });

  // LinkedIn Connection State
  const [linkedinConnected, setLinkedinConnected] = useState(false);
  const [linkedinUrn, setLinkedinUrn] = useState('');

  // Redirect if not signed in
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in');
    }
  }, [isLoaded, isSignedIn, router]);

  // Check for LinkedIn OAuth callback parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const linkedinSuccess = urlParams.get('linkedin_success');
    const linkedinUrnParam = urlParams.get('linkedin_urn');

    if (linkedinSuccess === 'true' && linkedinUrnParam) {
      localStorage.setItem('linkedin_user_urn', linkedinUrnParam);
      setLinkedinConnected(true);
      setLinkedinUrn(linkedinUrnParam);
      showToast.success('LinkedIn connected successfully!');
      window.history.replaceState({}, document.title, window.location.pathname);
      setStep(3); // Move to next step
    } else if (linkedinSuccess === 'false') {
      const error = urlParams.get('error') || 'Unknown error';
      showToast.error(`LinkedIn connection failed: ${error}`);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Check if already connected from a previous session
    const storedUrn = localStorage.getItem('linkedin_user_urn');
    if (storedUrn) {
      setLinkedinConnected(true);
      setLinkedinUrn(storedUrn);
    }
  }, []);

  useEffect(() => {
    if (!isLoaded || !userId) return;

    // Check if settings already exist
    const checkSettings = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/settings/${userId}`);
        if (response.data && !response.data.error) {
          setFormData(prev => ({
            ...prev,
            github_username: response.data.github_username || ''
          }));
        }
      } catch (e) {
        // No existing settings
      }
    };
    checkSettings();
  }, [isLoaded, userId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleConnectLinkedIn = async () => {
    if (!formData.linkedin_client_id || !formData.linkedin_client_secret) {
      showToast.error('Please enter LinkedIn Client ID and Secret first');
      return;
    }

    if (!userId) {
      showToast.error('User not authenticated');
      return;
    }

    const toastId = showToast.loading('Saving credentials & connecting to LinkedIn...');
    try {
      // First, save the credentials to the backend
      await axios.post(`${API_BASE}/api/settings`, {
        user_id: userId,
        linkedin_client_id: formData.linkedin_client_id,
        linkedin_client_secret: formData.linkedin_client_secret,
        groq_api_key: formData.groq_api_key || '',
        github_username: formData.github_username || '',
        unsplash_access_key: formData.unsplash_access_key || ''
      });

      // Check if backend is reachable
      await axios.get(`${API_BASE}/health`, { timeout: 2000 });
      showToast.dismiss(toastId);

      // Now redirect to OAuth with user_id for per-user credentials
      const redirectUri = `${window.location.origin}/auth/callback`;
      window.location.href = `${API_BASE}/auth/linkedin/start?redirect_uri=${encodeURIComponent(redirectUri)}&user_id=${encodeURIComponent(userId)}`;
    } catch (error: any) {
      showToast.dismiss(toastId);
      if (error.response) {
        showToast.error('Failed to save credentials: ' + (error.response.data?.error || error.message));
      } else {
        showToast.error('Backend server is unreachable. Please ensure the Python server is running.');
      }
    }
  };

  const handleComplete = async () => {
    if (!userId) return;

    setLoading(true);
    const toastId = showToast.loading('Saving your setup...');

    try {
      await axios.post(`${API_BASE}/api/settings`, {
        user_id: userId,
        linkedin_client_id: formData.linkedin_client_id,
        linkedin_client_secret: formData.linkedin_client_secret,
        groq_api_key: formData.groq_api_key,
        github_username: formData.github_username,
        unsplash_access_key: formData.unsplash_access_key,
        linkedin_user_urn: linkedinUrn
      });

      showToast.dismiss(toastId);
      showToast.success('Setup complete! Welcome aboard 🚀');

      setTimeout(() => {
        router.push('/dashboard');
      }, 1500);
    } catch (error: any) {
      showToast.dismiss(toastId);
      showToast.error('Failed to save settings: ' + (error.response?.data?.error || error.message));
      setLoading(false);
    }
  };

  // Individual field saving
  const [savingField, setSavingField] = useState<string | null>(null);

  const handleSaveField = async (fieldName: string) => {
    if (!userId) {
      showToast.error('User not authenticated');
      return;
    }

    setSavingField(fieldName);

    try {
      const payload: Record<string, string> = { user_id: userId };
      payload[fieldName] = formData[fieldName as keyof typeof formData];

      // Include other values to avoid overwriting
      if (fieldName !== 'groq_api_key' && formData.groq_api_key) {
        payload.groq_api_key = formData.groq_api_key;
      }
      if (fieldName !== 'github_username' && formData.github_username) {
        payload.github_username = formData.github_username;
      }
      if (fieldName !== 'unsplash_access_key' && formData.unsplash_access_key) {
        payload.unsplash_access_key = formData.unsplash_access_key;
      }
      if (linkedinUrn) {
        payload.linkedin_user_urn = linkedinUrn;
      }

      const response = await axios.post(`${API_BASE}/api/settings`, payload);

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      const fieldLabels: Record<string, string> = {
        groq_api_key: 'Groq API Key',
        github_username: 'GitHub Username',
        unsplash_access_key: 'Unsplash Key'
      };

      showToast.success(`${fieldLabels[fieldName] || fieldName} saved!`);
    } catch (error: any) {
      showToast.error(`Failed to save: ${error.message || 'Unknown error'}`);
    } finally {
      setSavingField(null);
    }
  };

  const nextStep = () => setStep(step + 1);
  const prevStep = () => setStep(step - 1);

  if (!isLoaded || !isSignedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary transition-colors duration-300 overflow-hidden relative">
      <SEOHead
        title="Setup - LinkedIn Post Bot"
        description="Initialize your AI-powered LinkedIn assistant"
      />

      {/* Background Ambience */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full bg-[url('/grid.svg')] opacity-[0.05] dark:opacity-[0.02]"></div>
        <div className="absolute -top-[20%] -right-[10%] w-[70vw] h-[70vw] bg-purple-500/20 rounded-full blur-3xl animate-blob mix-blend-multiply dark:mix-blend-screen"></div>
        <div className="absolute -bottom-[20%] -left-[10%] w-[70vw] h-[70vw] bg-blue-500/20 rounded-full blur-3xl animate-blob animation-delay-4000 mix-blend-multiply dark:mix-blend-screen"></div>
      </div>

      {/* Header */}
      <header className="relative z-50 border-b border-gray-200/50 dark:border-white/5 bg-white/50 dark:bg-black/20 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span className="font-bold text-xl tracking-tight">PostBot</span>
          </div>
          <ThemeToggle />
        </div>
      </header>

      <main className="relative z-10 max-w-4xl mx-auto px-6 py-16 flex flex-col items-center justify-center min-h-[calc(100vh-80px)]">

        {/* Progress Indicators */}
        <div className="flex items-center gap-4 mb-16">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center">
              <div className={`
                w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all duration-500
                ${step === s ? 'bg-blue-600 text-white shadow-lg ring-4 ring-blue-500/20 scale-110' :
                  step > s ? 'bg-green-500 text-white' : 'bg-gray-200 dark:bg-white/5 text-gray-500'}
              `}>
                {step > s ? '✓' : s}
              </div>
              {s < 4 && (
                <div className={`w-12 h-1 mx-3 rounded-full transition-all duration-500 ${step > s ? 'bg-green-500' : 'bg-gray-200 dark:bg-white/5'}`} />
              )}
            </div>
          ))}
        </div>

        {/* Card Container */}
        <div className="w-full bg-white/80 dark:bg-white/5 backdrop-blur-xl border border-gray-200 dark:border-white/10 rounded-3xl shadow-2xl overflow-hidden min-h-[500px] flex flex-col">

          {/* Step 1: Welcome & Overview */}
          <div className={`flex-1 p-10 flex flex-col transition-opacity duration-500 ${step === 1 ? 'opacity-100' : 'hidden opacity-0'}`}>
            <div className="flex-1 flex flex-col items-center justify-center text-center space-y-8">
              <div className="w-24 h-24 bg-gradient-to-tr from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-xl animate-float">
                <span className="text-4xl">🚀</span>
              </div>
              <div>
                <h1 className="text-4xl font-extrabold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent mb-4">
                  Let's set up your assistant
                </h1>
                <p className="text-lg text-gray-600 dark:text-gray-400 max-w-lg mx-auto leading-relaxed">
                  Connect your accounts to start generating AI-powered LinkedIn content from your development activity.
                </p>
              </div>

              <div className="grid grid-cols-3 gap-4 w-full max-w-lg">
                <div className="p-4 rounded-2xl bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-white/5 text-left">
                  <div className="font-semibold mb-1 text-gray-900 dark:text-white">LinkedIn</div>
                  <div className="text-sm text-gray-500">Post directly</div>
                </div>
                <div className="p-4 rounded-2xl bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-white/5 text-left">
                  <div className="font-semibold mb-1 text-gray-900 dark:text-white">Groq AI</div>
                  <div className="text-sm text-gray-500">Generate content</div>
                </div>
                <div className="p-4 rounded-2xl bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-white/5 text-left">
                  <div className="font-semibold mb-1 text-gray-900 dark:text-white">GitHub</div>
                  <div className="text-sm text-gray-500">Track commits</div>
                </div>
              </div>

              <button
                onClick={nextStep}
                className="w-full max-w-md bg-gray-900 dark:bg-white text-white dark:text-gray-900 py-4 rounded-xl font-bold text-lg hover:scale-[1.02] active:scale-95 transition-all shadow-lg hover:shadow-xl"
              >
                Start Setup
              </button>
            </div>
          </div>

          {/* Step 2: Connect LinkedIn */}
          <div className={`flex-1 p-10 flex flex-col transition-opacity duration-500 ${step === 2 ? 'opacity-100' : 'hidden opacity-0'}`}>
            <h2 className="text-2xl font-bold mb-2">Connect LinkedIn</h2>
            <p className="text-gray-500 dark:text-gray-400 mb-6">Required for posting to your LinkedIn profile.</p>

            {linkedinConnected ? (
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-500/30 rounded-2xl p-6 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-green-600 dark:text-green-400 font-semibold">LinkedIn Connected!</p>
                    <p className="text-green-500/70 text-sm">Account ready for posting</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-6 flex-1">
                <p className="text-sm text-gray-500">
                  Enter your LinkedIn Developer App credentials.{' '}
                  <a href="https://www.linkedin.com/developers/apps" target="_blank" className="text-blue-500 underline hover:text-blue-600">
                    Get credentials →
                  </a>
                </p>

                <div className="grid md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    name="linkedin_client_id"
                    placeholder="Client ID"
                    value={formData.linkedin_client_id}
                    onChange={handleChange}
                    className="w-full bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-white/10 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                  />
                  <input
                    type="password"
                    name="linkedin_client_secret"
                    placeholder="Client Secret"
                    value={formData.linkedin_client_secret}
                    onChange={handleChange}
                    className="w-full bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-white/10 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                  />
                </div>

                <button
                  onClick={handleConnectLinkedIn}
                  disabled={!formData.linkedin_client_id || !formData.linkedin_client_secret}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white py-4 rounded-xl font-bold transition-all flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                  </svg>
                  Connect LinkedIn Account
                </button>
              </div>
            )}

            <div className="flex gap-4 pt-6 mt-auto border-t border-gray-200 dark:border-white/10">
              <button onClick={prevStep} className="px-6 py-3 rounded-xl border border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5 font-medium transition-colors">
                Back
              </button>
              <button
                onClick={nextStep}
                disabled={!linkedinConnected}
                className="flex-1 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-xl font-bold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                Continue
              </button>
            </div>
          </div>

          {/* Step 3: Credentials */}
          <div className={`flex-1 p-10 flex flex-col transition-opacity duration-500 ${step === 3 ? 'opacity-100' : 'hidden opacity-0'}`}>
            <h2 className="text-2xl font-bold mb-2">API Keys & Profile</h2>
            <p className="text-gray-500 dark:text-gray-400 mb-8">Enter your API keys to enable the bot's superpowers.</p>

            <div className="space-y-6 flex-1 overflow-y-auto pr-2 custom-scrollbar">

              {/* Groq UI */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400 font-semibold">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  Groq API Key (AI Model)
                </div>
                <input
                  type="password"
                  name="groq_api_key"
                  placeholder="gsk_..."
                  value={formData.groq_api_key}
                  onChange={handleChange}
                  className="w-full bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-white/10 rounded-xl px-4 py-3 focus:ring-2 focus:ring-purple-500 outline-none transition-all font-mono text-sm"
                />
                <div className="flex items-center justify-between mt-2">
                  <p className="text-xs text-gray-500">
                    Free AI inference. Get key from <a href="https://console.groq.com/keys" target="_blank" className="underline hover:text-purple-500">Groq Console</a>
                  </p>
                  <button
                    type="button"
                    onClick={() => handleSaveField('groq_api_key')}
                    disabled={!formData.groq_api_key || savingField === 'groq_api_key'}
                    className="px-3 py-1.5 bg-purple-500 hover:bg-purple-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white text-xs font-medium rounded-lg transition-all flex items-center gap-1"
                  >
                    {savingField === 'groq_api_key' ? '⏳' : '💾'} Save
                  </button>
                </div>
              </div>

              <div className="h-px bg-gray-200 dark:bg-white/10 my-6" />

              {/* GitHub */}
              <div className="space-y-4">
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">GitHub Username</label>
                <div className="relative">
                  <span className="absolute left-4 top-3.5 text-gray-400 font-mono">github.com/</span>
                  <input
                    type="text"
                    name="github_username"
                    placeholder="username"
                    value={formData.github_username}
                    onChange={handleChange}
                    className="w-full bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-white/10 rounded-xl pl-28 pr-4 py-3 focus:ring-2 focus:ring-green-500 outline-none transition-all font-mono"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => handleSaveField('github_username')}
                  disabled={!formData.github_username || savingField === 'github_username'}
                  className="px-3 py-1.5 bg-gray-600 hover:bg-gray-500 disabled:bg-gray-400 disabled:cursor-not-allowed text-white text-xs font-medium rounded-lg transition-all flex items-center gap-1"
                >
                  {savingField === 'github_username' ? '⏳' : '💾'} Save GitHub Username
                </button>
              </div>

              <div className="h-px bg-gray-200 dark:bg-white/10 my-6" />

              {/* Unsplash (Optional) */}
              <div className="space-y-4">
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">Unsplash Access Key <span className="text-gray-400 font-normal">(Optional)</span></label>
                <input
                  type="password"
                  name="unsplash_access_key"
                  placeholder="For adding images to posts..."
                  value={formData.unsplash_access_key}
                  onChange={handleChange}
                  className="w-full bg-gray-50 dark:bg-black/20 border border-gray-200 dark:border-white/10 rounded-xl px-4 py-3 focus:ring-2 focus:ring-orange-500 outline-none transition-all"
                />
                <button
                  type="button"
                  onClick={() => handleSaveField('unsplash_access_key')}
                  disabled={!formData.unsplash_access_key || savingField === 'unsplash_access_key'}
                  className="px-3 py-1.5 bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white text-xs font-medium rounded-lg transition-all flex items-center gap-1"
                >
                  {savingField === 'unsplash_access_key' ? '⏳' : '💾'} Save Unsplash Key
                </button>
              </div>
            </div>

            <div className="flex gap-4 pt-6 mt-4 border-t border-gray-200 dark:border-white/10">
              <button onClick={prevStep} className="px-6 py-3 rounded-xl border border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5 font-medium transition-colors">
                Back
              </button>
              <button
                onClick={nextStep}
                disabled={!formData.groq_api_key || !formData.github_username}
                className="flex-1 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-xl font-bold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                Continue
              </button>
            </div>
          </div>

          {/* Step 4: Finish */}
          <div className={`flex-1 p-10 flex flex-col transition-opacity duration-500 ${step === 4 ? 'opacity-100' : 'hidden opacity-0'}`}>
            <div className="flex-1 flex flex-col items-center justify-center text-center space-y-8">
              <div className="w-24 h-24 bg-gradient-to-tr from-green-400 to-emerald-500 rounded-full flex items-center justify-center shadow-xl">
                <span className="text-4xl">✨</span>
              </div>
              <div>
                <h1 className="text-4xl font-extrabold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent mb-4">
                  You're all set!
                </h1>
                <p className="text-lg text-gray-600 dark:text-gray-400 max-w-lg mx-auto leading-relaxed">
                  Your accounts are connected. Click below to save and start generating posts.
                </p>
              </div>

              <div className="w-full max-w-md space-y-4">
                <div className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-500/30">
                  <span className="text-green-600 dark:text-green-400 font-medium">LinkedIn Connected</span>
                  <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                </div>
                <div className="flex items-center justify-between p-4 bg-purple-50 dark:bg-purple-900/20 rounded-xl border border-purple-200 dark:border-purple-500/30">
                  <span className="text-purple-600 dark:text-purple-400 font-medium">Groq AI Ready</span>
                  <svg className="w-5 h-5 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                </div>
                <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/20 rounded-xl border border-gray-200 dark:border-gray-500/30">
                  <span className="text-gray-600 dark:text-gray-400 font-medium">GitHub: {formData.github_username}</span>
                  <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                </div>
              </div>
            </div>

            <div className="flex gap-4 pt-6 mt-8 border-t border-gray-200 dark:border-white/10">
              <button onClick={prevStep} className="px-6 py-3 rounded-xl border border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5 font-medium transition-colors">
                Back
              </button>
              <button
                onClick={handleComplete}
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-purple-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    Finishing Up...
                  </>
                ) : 'Complete Setup & Go to Dashboard ✨'}
              </button>
            </div>
          </div>

        </div>

        {/* Footer Help Links */}
        <div className="mt-6 flex items-center justify-between px-4 py-3 bg-white/5 dark:bg-black/20 rounded-xl border border-gray-200/50 dark:border-white/10">
          <p className="text-gray-500 dark:text-gray-400 text-sm">Need help setting up?</p>
          <div className="flex gap-4">
            <a href="/documentation" className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors">
              📚 Documentation
            </a>
            <a href="/support" className="text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 transition-colors">
              💬 Support
            </a>
          </div>
        </div>

      </main>

      <style jsx global>{`
        @keyframes blob {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
        }
        .animate-blob {
          animation: blob 10s infinite;
        }
        .animation-delay-4000 {
           animation-delay: 4s;
        }
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
          100% { transform: translateY(0px); }
        }
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(156, 163, 175, 0.5);
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
}
