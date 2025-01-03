import { getServerSession } from 'next-auth';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';
import { authFetch } from '@/app/api/authFetch';

export async function DELETE(req: Request, { params }: { params: Promise<{ transactionId: string }> }) {
    const session = await getServerSession(authOptions);

    const { transactionId } = await params;

    if (!transactionId) {
        return new Response(JSON.stringify({ error: 'Transaction ID is required' }), { status: 400 });
    }

    return authFetch(session, `transactions/${transactionId}`, {
        method: 'DELETE',
    });
}
