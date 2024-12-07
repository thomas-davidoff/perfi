import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
    const cookieStore = await cookies(); // Await the promise
    const accessToken = cookieStore.get('access_token')?.value;

    if (!accessToken) {
        // No token present, redirect to login
        redirect('/login');
    }

    // Fetch protected data from Flask backend
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/transactions`, {
        headers: {
            Authorization: `Bearer ${accessToken}`
        },
        // Important: enable cookies to be sent with fetch
        cache: 'no-store',
    });

    if (res.status === 401) {
        // Token might be invalid or expired.
        // You could attempt a token refresh here if you wanted.
        redirect('/login');
    }

    const data = await res.json();

    return (
        <div>
            <h1>Welcome to Your Dashboard</h1>
            <h2>Transactions</h2>
            <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
    );
}
