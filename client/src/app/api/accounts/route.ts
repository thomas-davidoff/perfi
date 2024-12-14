import { getServerSession } from 'next-auth';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';
import { authFetch } from '@/app/api/authFetch'

export async function GET() {
    const session = await getServerSession(authOptions);
    return authFetch(session, 'accounts');
}
