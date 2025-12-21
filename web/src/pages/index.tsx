import { useRef, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import dynamic from 'next/dynamic';
import { SignedIn, SignedOut, UserButton, useUser } from "@clerk/nextjs";
import SEOHead from '@/components/SEOHead';
import ThemeToggle from '@/components/ThemeToggle';


export default function Home() {
  const router = useRouter();
  const { isSignedIn } = useUser();

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary transition-colors duration-300 overflow-x-hidden selection:bg-purple-500/30">
      <SEOHead
        title="LinkedIn Post Bot - Turn Commits into Authority"
        description="The AI agent that writes engaging LinkedIn posts from your GitHub activity. 10x faster."
      />

      {/* Header */}
      <header className="fixed top-0 w-full z-50 bg-white/80 dark:bg-black/50 backdrop-blur-xl border-b border-gray-200/50 dark:border-white/5">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400">
              PostBot
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600 dark:text-gray-300">
            <a href="#features" className="hover:text-blue-600 dark:hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-blue-600 dark:hover:text-white transition-colors">How it works</a>
            <a href="#testimonials" className="hover:text-blue-600 dark:hover:text-white transition-colors">Testimonials</a>
          </nav>

          <div className="flex items-center gap-4">
            <ThemeToggle />

            <SignedOut>
              <button
                onClick={() => router.push('/sign-in')}
                className="text-sm font-bold text-gray-700 dark:text-gray-200 hover:text-blue-600 transition-colors"
              >
                Sign In
              </button>
              <button
                onClick={() => router.push('/sign-up')}
                className="bg-gray-900 dark:bg-white text-white dark:text-gray-900 px-4 py-2 rounded-lg text-sm font-bold hover:opacity-90 transition-all hover:scale-105"
              >
                Get Started Free
              </button>
            </SignedOut>

            <SignedIn>
              <button
                onClick={() => router.push('/dashboard')}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-700 transition-all font-mono"
              >
                Dashboard &rarr;
              </button>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>
        </div>
      </header>

      <main className="pt-32 pb-16 px-6">
        {/* HERO SECTION */}
        <div className="max-w-7xl mx-auto text-center relative">

          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-500/30 text-blue-600 dark:text-blue-300 text-sm font-medium mb-8 animate-fade-in-up">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            New: GitHub Actions Integration
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 animate-fade-in-up animation-delay-100">
            <span className="block text-gray-900 dark:text-white">Turn GitHub Activity</span>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600">
              Into LinkedIn Authority
            </span>
          </h1>

          {/* Subhead */}
          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-in-up animation-delay-200">
            The AI agent that automatically writes engaging LinkedIn posts from your commits, PRs, and releases.
            <span className="block text-gray-900 dark:text-white font-semibold mt-2">Build your personal brand 10x faster.</span>
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20 animate-fade-in-up animation-delay-300">
            <button
              onClick={() => router.push(isSignedIn ? '/dashboard' : '/sign-up')}
              className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-bold text-lg hover:shadow-xl hover:shadow-blue-500/25 hover:scale-105 transition-all duration-300 flex items-center justify-center gap-2"
            >
              start generating free
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
            <a
              href="https://github.com/cliff-de-tech/Linkedin-Post-Bot"
              target="_blank"
              rel="noopener noreferrer"
              className="w-full sm:w-auto px-8 py-4 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 text-gray-700 dark:text-gray-300 rounded-xl font-semibold text-lg hover:bg-gray-50 dark:hover:bg-white/10 transition-all flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5 text-gray-500" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
              View on GitHub
            </a>
          </div>

          {/* Trust Signals */}
          <div className="flex items-center justify-center gap-6 text-sm text-gray-500 dark:text-gray-400 mb-16 animate-fade-in-up animation-delay-400">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>No credit card required</span>
            </div>
            <div className="hidden sm:flex items-center gap-2">
              <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm-2 16h-2v-6h2v6zm-1-6.891c-.607 0-1.1-.496-1.1-1.109 0-.612.492-1.109 1.1-1.109s1.1.497 1.1 1.109c0 .613-.492 1.109-1.1 1.109zm8 6.891h-1.998v-2.861c0-1.881-2.002-1.722-2.002 0v2.861h-2v-6h2v1.093c.872-1.616 4-1.736 4 1.548v3.359z" />
              </svg>
              <span>LinkedIn Safe</span>
            </div>
            <div className="flex items-center gap-2">
              <span>⭐ 4.9/5 from Developers</span>
            </div>
          </div>

          {/* 3D Dashboard Mockup */}
          <div className="relative mx-auto max-w-5xl animate-float-slow">
            <div className="absolute inset-0 bg-gradient-to-t from-bg-primary via-transparent to-transparent z-10 bottom-0 h-40"></div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl shadow-2xl overflow-hidden transform perspective-1000 rotate-x-6 transition-transform duration-700 hover:rotate-x-0">
              {/* Mockup Header */}
              <div className="bg-gray-800 px-4 py-3 flex items-center gap-2 border-b border-gray-700">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
                <div className="flex-1 text-center">
                  <div className="bg-gray-900 rounded-md px-3 py-1 text-xs text-gray-400 inline-block font-mono w-64">
                    postbot.app/dashboard
                  </div>
                </div>
              </div>

              {/* Mockup Content */}
              <div className="grid grid-cols-12 h-[500px] bg-gray-900 text-left">
                {/* Sidebar */}
                <div className="col-span-2 border-r border-gray-800 p-4 space-y-4 hidden sm:block">
                  <div className="h-4 w-20 bg-gray-800 rounded"></div>
                  <div className="space-y-2 pt-4">
                    {[1, 2, 3, 4].map(i => (
                      <div key={i} className="h-8 w-full bg-gray-800/50 rounded flex items-center px-2">
                        <div className="w-4 h-4 bg-gray-700 rounded mr-2"></div>
                        <div className="h-2 w-16 bg-gray-700 rounded"></div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Main Content */}
                <div className="col-span-12 sm:col-span-10 p-6 sm:p-8">
                  <div className="flex justify-between items-center mb-8">
                    <div>
                      <div className="h-6 w-48 bg-gray-800 rounded mb-2"></div>
                      <div className="h-3 w-64 bg-gray-800/50 rounded"></div>
                    </div>
                    <div className="h-10 w-32 bg-blue-600 rounded"></div>
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    {/* Generated Post Card */}
                    <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-full bg-gray-700"></div>
                        <div>
                          <div className="h-3 w-24 bg-gray-700 rounded mb-1"></div>
                          <div className="h-2 w-16 bg-gray-700/50 rounded"></div>
                        </div>
                      </div>
                      <div className="space-y-2 mb-4">
                        <div className="h-2 w-full bg-gray-700/50 rounded"></div>
                        <div className="h-2 w-full bg-gray-700/50 rounded"></div>
                        <div className="h-2 w-3/4 bg-gray-700/50 rounded"></div>
                      </div>
                      <div className="h-48 w-full bg-gray-700/30 rounded border border-dashed border-gray-700 flex items-center justify-center text-gray-600 text-sm">
                        AI Generated Image
                      </div>
                    </div>

                    {/* GitHub Activity Card */}
                    <div className="bg-gray-800/30 border border-gray-800 rounded-xl p-6">
                      <div className="h-4 w-32 bg-gray-700 rounded mb-4"></div>
                      <div className="space-y-3">
                        {[1, 2, 3].map(i => (
                          <div key={i} className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg">
                            <div className="w-8 h-8 rounded bg-gray-700 flex-shrink-0"></div>
                            <div className="flex-1">
                              <div className="h-2 w-full bg-gray-700 rounded mb-1"></div>
                              <div className="h-2 w-24 bg-gray-700/50 rounded"></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* LOGO STRIP */}
        <div className="mt-20 border-t border-b border-gray-200 dark:border-white/5 py-10 bg-gray-50/50 dark:bg-white/5 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-6 text-center">
            <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-8">Trusted by developers from</p>
            <div className="flex flex-wrap justify-center items-center gap-12 md:gap-20 opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
              {/* Replaced with text/svg placeholders for logos to avoid external image deps */}
              <div className="flex items-center gap-2 font-bold text-xl font-sans"><svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" /></svg> GitHub</div>
              <div className="flex items-center gap-2 font-bold text-xl font-sans"><svg className="w-6 h-6" viewBox="0 0 76 65" fill="currentColor"><path d="M37.5274 0L75.0548 65H0L37.5274 0Z" /></svg> Vercel</div>
              <div className="flex items-center gap-2 font-bold text-xl font-sans">Groq Cloud</div>
              <div className="flex items-center gap-2 font-bold text-xl font-sans text-[#0A66C2]">LinkedIn</div>
            </div>
          </div>
        </div>

        {/* FEATURES GRID */}
        <div id="features" className="max-w-7xl mx-auto py-24">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">Everything you need to grow</h2>
            <p className="text-xl text-gray-500 dark:text-gray-400">Automate your personal brand while you code.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { title: 'Code to Content', desc: 'Automatically turn your Git commits and PRs into engaging stories.', icon: '🤖' },
              { title: 'Brand Consistency', desc: 'Maintain a consistent posting schedule without breaking your flow.', icon: '📅' },
              { title: 'Developer Focused', desc: 'Understands tech stack, languages, and open source culture.', icon: '⚡' }
            ].map((feature, i) => (
              <div key={i} className="group p-8 rounded-2xl bg-white dark:bg-white/5 border border-gray-100 dark:border-white/10 hover:border-blue-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10">
                <div className="w-14 h-14 bg-blue-50 dark:bg-blue-900/20 rounded-xl flex items-center justify-center text-3xl mb-6 group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                <p className="text-gray-500 dark:text-gray-400 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA SECTION */}
        <div className="max-w-5xl mx-auto mt-12 mb-20 p-12 rounded-3xl bg-gradient-to-br from-blue-600 to-purple-700 text-center text-white relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-full bg-[url('/grid.svg')] opacity-10"></div>
          <div className="relative z-10">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">Ready to amplify your career?</h2>
            <p className="text-xl text-blue-100 mb-10 max-w-2xl mx-auto">
              Join thousands of developers turning their code into opportunities.
            </p>
            <button
              onClick={() => router.push(isSignedIn ? '/dashboard' : '/sign-up')}
              className="px-10 py-5 bg-white text-blue-600 rounded-xl font-bold text-lg hover:bg-blue-50 transition-all hover:scale-105 shadow-xl"
            >
              Get Started for Free
            </button>
            <p className="mt-6 text-sm text-blue-200 opacity-80">No credit card required • Open Source • Secure</p>
          </div>
        </div>

      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-white/10 py-12 bg-gray-50 dark:bg-black/20">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center text-sm text-gray-500 dark:text-gray-400">
          <div className="mb-4 md:mb-0">
            © 2024 PostBot. Open Source under MIT License.
          </div>
          <div className="flex gap-6">
            <a href="#" className="hover:text-blue-500 transition-colors">Privacy</a>
            <a href="#" className="hover:text-blue-500 transition-colors">Terms</a>
            <a href="https://github.com/cliff-de-tech/Linkedin-Post-Bot" target="_blank" rel="noopener noreferrer" className="hover:text-blue-500 transition-colors">GitHub</a>
          </div>
        </div>
      </footer>

      <style jsx global>{`
        .perspective-1000 {
          perspective: 1000px;
        }
        .rotate-x-6 {
          transform: rotateX(6deg);
        }
        .rotate-x-0 {
          transform: rotateX(0deg);
        }
        @keyframes float-slow {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        .animate-float-slow {
          animation: float-slow 6s ease-in-out infinite;
        }
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-up {
          animation: fadeInUp 0.8s ease-out forwards;
          opacity: 0;
        }
        .animation-delay-100 { animation-delay: 0.1s; }
        .animation-delay-200 { animation-delay: 0.2s; }
        .animation-delay-300 { animation-delay: 0.3s; }
        .animation-delay-400 { animation-delay: 0.4s; }
      `}</style>
    </div>
  );
}
