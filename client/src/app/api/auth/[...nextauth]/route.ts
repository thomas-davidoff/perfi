import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { API_BASE_URL } from "@/app/constants";

export const authOptions = {
    providers: [
        CredentialsProvider({
            name: "Credentials",
            credentials: {
                username: { label: "Username", type: "text" },
                password: { label: "Password", type: "password" },
            },
            async authorize(credentials) {
                const res = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: credentials?.username,
                        password: credentials?.password
                    })
                });

                const data = await res.json();
                if (!data?.access_token) {
                    throw new Error(data.msg || "Invalid username or password");
                }

                return {
                    id: data.id,
                    name: data.user.name,
                    email: data.user.email,
                    access_token: data.access_token,
                    refresh_token: data.refresh_token,
                    access_token_expires: new Date(data.access_token_expires),
                    refresh_token_expires: new Date(data.refresh_token_expires)
                };
            },
        }),
    ],
    callbacks: {
        async jwt({ token, user }) {
            if (user) {
                token.access_token = user.access_token;
                token.refresh_token = user.refresh_token;
                token.access_token_expires = user.access_token_expires;
                token.refresh_token_expires = user.refresh_token_expires;
            }

            if (new Date() >= new Date(token.access_token_expires)) {
                try {
                    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/refresh`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token.refresh_token}`
                        },
                    });

                    if (!response.ok) {
                        throw new Error('Failed to refresh access token');
                    }

                    const refreshedTokens = await response.json();

                    token.access_token = refreshedTokens.access_token;
                    token.access_token_expires = new Date(refreshedTokens.access_token_expires);
                } catch (error) {
                    console.error("Error refreshing access token:", error);
                    token.error = "RefreshAccessTokenError";
                }
            }

            return token;
        },
        async session({ session, token }) {
            session.access_token = token.access_token;
            session.error = token.error;
            return session;
        },
    },
    secret: process.env.NEXTAUTH_SECRET,
    pages: {
        signIn: '/login'
    }
};

export const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
