import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
            <SignUp path="/sign-up" routing="path" signInUrl="/sign-in" />
        </div>
    );
}
