import { getServerSession } from 'next-auth';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';
import { authFetch } from '@/app/api/authFetch';

export async function GET() {
    const session = await getServerSession(authOptions);
    return authFetch(session, 'transactions');
}

export async function POST(req: Request) {
    const session = await getServerSession(authOptions);
    const body = await req.json();

    return authFetch(session, 'transactions', {
        method: 'POST',
        body: JSON.stringify(body),
        headers: {
            'Content-Type': 'application/json',
        },
    });
}
