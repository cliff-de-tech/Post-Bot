
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Dashboard from '@/pages/dashboard';
import { useUser, useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/router';
import { useDashboardData } from '@/hooks/useDashboardData';
import { generatePreview } from '@/lib/api';

// --- Mocks ---

// Mock Clerk
jest.mock('@clerk/nextjs', () => ({
  useUser: jest.fn(),
  useAuth: jest.fn(),
  UserButton: () => <div data-testid="user-button">UserButton</div>,
}));

// Mock Next Router
jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

// Mock Custom Hooks
jest.mock('@/hooks/useDashboardData', () => ({
  useDashboardData: jest.fn(),
}));

// Mock API
jest.mock('@/lib/api', () => ({
  generatePreview: jest.fn(),
  publishPost: jest.fn(),
  schedulePost: jest.fn(),
  api: {
    post: jest.fn().mockResolvedValue({ data: { authenticated: true } }),
    get: jest.fn().mockResolvedValue({ data: { posts: [] } }),
  },
}));

// Mock Components that might cause issues in simple tests
jest.mock('@/components/dashboard/StatsOverview', () => ({
  StatsOverview: () => <div data-testid="stats-overview">Stats</div>
}));
jest.mock('@/components/dashboard/ActivityFeed', () => ({
  ActivityFeed: () => <div data-testid="activity-feed">ActivityFeed</div>
}));
jest.mock('@/features/post-generation/components/PostEditor', () => ({
  PostEditor: ({ onGenerate }: any) => (
    <div data-testid="post-editor">
      <button onClick={() => onGenerate('groq')} data-testid="generate-btn">
        Generate Preview
      </button>
    </div>
  )
}));
jest.mock('@/features/post-generation/components/PostPreview', () => ({
  PostPreview: ({ preview }: any) => <div data-testid="post-preview">{preview}</div>
}));
jest.mock('@/components/ThemeToggle', () => ({
  __esModule: true,
  default: () => <div data-testid="theme-toggle">ThemeToggle</div>
}));
jest.mock('@/components/ui/TierBadge', () => ({
  __esModule: true,
  default: () => <div data-testid="tier-badge">TierBadge</div>
}));
jest.mock('@/components/ui/UsageCounter', () => ({
    __esModule: true,
    default: () => <div data-testid="usage-counter">Usage</div>
}));

// Mock remaining dashboard components
jest.mock('@/components/dashboard/Analytics', () => ({
  __esModule: true,
  default: () => <div data-testid="analytics">Analytics</div>
}));
jest.mock('@/components/dashboard/BotModePanel', () => ({
  BotModePanel: () => <div data-testid="bot-mode-panel">BotMode</div>
}));
jest.mock('@/components/ui/AIStatusMessage', () => ({
  AIStatusMessage: () => null,
  useAIStatus: () => ({
    messages: [],
    isActive: false,
    show: jest.fn(),
    update: jest.fn(),
    complete: jest.fn(),
    error: jest.fn(),
    dismiss: jest.fn(),
  }),
}));
jest.mock('@/components/dashboard/DashboardSkeleton', () => ({
  __esModule: true,
  default: () => <div data-testid="skeleton">Loading...</div>
}));
jest.mock('@/components/dashboard/FeedbackManager', () => ({
  FeedbackManager: () => null
}));
jest.mock('@/components/ui/FeatureGate', () => ({
  __esModule: true,
  default: ({ children }: any) => <>{children}</>
}));
jest.mock('@/components/SEOHead', () => ({
  __esModule: true,
  default: () => null
}));
jest.mock('@/lib/toast', () => ({
  showToast: jest.fn(),
}));
jest.mock('@/store/useDraftStore', () => ({
  useDraftStore: () => ({
    context: { type: 'push', commits: 3, repo: 'my-project', full_repo: 'user/my-project', date: '2 hours ago' },
    setContext: jest.fn(),
    preview: '',
    setPreview: jest.fn(),
    isEditing: false,
    setIsEditing: jest.fn(),
    loading: false,
    setLoading: jest.fn(),
    status: '',
    setStatus: jest.fn(),
    selectedImage: null,
    setSelectedImage: jest.fn(),
    reset: jest.fn(),
  }),
}));


describe('Dashboard Component', () => {
  const mockPush = jest.fn();

  afterAll(() => {
    jest.clearAllTimers();
  });

  beforeEach(() => {
    jest.clearAllMocks();

    // Setup Router Mock
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
      isReady: true,
      query: {},
    });

    // Setup User Mock (Authenticated)
    (useUser as jest.Mock).mockReturnValue({
      isLoaded: true,
      isSignedIn: true,
      user: { id: 'test_user_123', fullName: 'Test User' },
    });

    (useAuth as jest.Mock).mockReturnValue({
      getToken: jest.fn().mockResolvedValue('fake_token'),
    });

    // Setup Data Hook Mock
    (useDashboardData as jest.Mock).mockReturnValue({
      stats: { posts_generated: 10 },
      posts: [],
      usage: { tier: 'free', posts_remaining: 5 },
      templates: [],
      githubActivities: [],
      githubUsername: '',
      personaComplete: true,
      firstActivityContext: null,
      isLoadingStats: false,
      isLoadingGithub: false,
      isLoadingPosts: false,
      refetchStats: jest.fn(),
      refetchPosts: jest.fn(),
      refetchAll: jest.fn(),
    });

    // Mock localStorage
    Storage.prototype.getItem = jest.fn((key) => {
      if (key === 'linkedin_user_urn') return 'urn:li:person:123';
      return null;
    });
  });

  it('renders the dashboard when authenticated', async () => {
    render(<Dashboard />);
    
    // Wait for the async auth check to resolve and re-render
    await waitFor(() => {
      expect(screen.getByText('Content Generator')).toBeInTheDocument();
    });
    
    // Check for mocked child components
    expect(screen.getByTestId('stats-overview')).toBeInTheDocument();
    expect(screen.getByTestId('activity-feed')).toBeInTheDocument();
  });

  it('calls generatePreview when generate button is clicked', async () => {
    // Mock API response
    (generatePreview as jest.Mock).mockResolvedValue({
      post: 'This is a generated post preview',
      provider: 'groq'
    });

    render(<Dashboard />);

    // Wait for the async auth check to resolve and dashboard to render
    await waitFor(() => {
      expect(screen.getByTestId('generate-btn')).toBeInTheDocument();
    });

    // Find and click the generate button (inside our mocked PostEditor)
    const generateBtn = screen.getByTestId('generate-btn');
    fireEvent.click(generateBtn);

    // Verify API call was made with correct parameters
    await waitFor(() => {
      expect(generatePreview).toHaveBeenCalledWith(
        expect.objectContaining({
          user_id: 'test_user_123',
          model: 'groq'
        }),
        'fake_token'
      );
    });
  });

  it('redirects to sign-in if not authenticated', () => {
    // Setup User Mock (Not Authenticated)
    (useUser as jest.Mock).mockReturnValue({
      isLoaded: true,
      isSignedIn: false,
      user: null,
    });

    render(<Dashboard />);

    // Should redirect
    expect(mockPush).toHaveBeenCalledWith('/sign-in');
  });
});
