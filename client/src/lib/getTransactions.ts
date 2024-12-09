import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { Transaction } from "@/types";

export async function getTransactions(): Promise<Transaction[]> {
    const session = await getServerSession(authOptions);

    if (!session?.access_token) {
        throw new Error("Not authenticated or no access token available");
    }
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/transactions`, {
        headers: {
            Authorization: `Bearer ${session.access_token}`,
        },
        cache: 'no-store',
    });

    if (!res.ok) {
        throw new Error("Failed to fetch transactions");
    }

    return res.json();
}
