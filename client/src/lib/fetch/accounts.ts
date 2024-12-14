import { Account } from "@/types";
/**
 * Fetch transactions from the API.
 * @returns Promise<Transaction[]>
 */
export async function fetchAccounts(): Promise<Account[]> {
    const res = await fetch('/api/accounts', { cache: 'no-store' });
    if (!res.ok) {
        throw new Error('Failed to fetch accounts');
    }
    return res.json();
}
