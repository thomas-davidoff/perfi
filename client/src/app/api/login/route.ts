import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
    const { username, password } = await req.json();

    // Call your Flask backend for authentication
    const resp = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    console.log(JSON.stringify({ username, password }))

    if (!resp.ok) {
        return NextResponse.json({ error: 'Invalid credentials' }, { status: 401 });
    }

    const data = await resp.json();
    const { access_token, refresh_token } = data;

    // Set tokens as HTTP-only cookies
    const response = NextResponse.json({ success: true });

    // Secure these cookies in production with `secure: true` and proper domain
    response.cookies.set('access_token', access_token, {
        httpOnly: true,
        sameSite: 'strict',
        path: '/',
        secure: process.env.NODE_ENV === 'production',
    });

    response.cookies.set('refresh_token', refresh_token, {
        httpOnly: true,
        sameSite: 'strict',
        path: '/',
        secure: process.env.NODE_ENV === 'production',
    });

    return response;
}
