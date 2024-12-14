import { NextResponse } from 'next/server';
import { API_BASE_URL } from '@/app/constants';

interface Session {
    access_token?: string;
}

export async function authFetch(
    session: Session | null,
    endpoint: string,
    options: RequestInit = {}
) {
    if (!session?.access_token) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
            ...options,
            headers: {
                Authorization: `Bearer ${session.access_token}`,
                ...options.headers,
            },
        });

        if (!response.ok) {
            const errorDetails = await response.json();
            console.error(`Error in ${endpoint} fetch:`, errorDetails);
            return NextResponse.json(
                { error: `Failed to fetch ${endpoint}`, details: errorDetails },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error(`Error in ${endpoint} request:`, error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
