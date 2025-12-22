import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isProtectedRoute = createRouteMatcher([
    '/dashboard(.*)',
    '/settings(.*)',
    '/onboarding(.*)'
]);

export default clerkMiddleware(async (auth, req) => {
    // DEV TEST MODE (DISABLED): Uncomment to bypass auth with ?test=true
    // const url = new URL(req.url);
    // const isTestMode = url.searchParams.get('test') === 'true';
    // if (isTestMode) {
    //     console.log('🧪 DEV TEST MODE: Skipping auth for', req.url);
    //     return;
    // }

    if (isProtectedRoute(req)) await auth.protect();
});

export const config = {
    matcher: ["/((?!.*\\..*|_next).*)", "/", "/(api|trpc)(.*)"],
};
