'use client';

import { LoginForm } from './login-form';

export default function LoginPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="w-full max-w-md p-8 bg-white shadow-md rounded">
                <LoginForm />
            </div>
        </div>
    );
}
