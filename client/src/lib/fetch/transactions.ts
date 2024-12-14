import { Transaction, TransactionPost } from "@/types";
/**
 * Fetch transactions from the API.
 * @returns Promise<Transaction[]>
 */
export async function fetchTransactions(): Promise<Transaction[]> {
    const res = await fetch('/api/transactions', { cache: 'no-store' });
    if (!res.ok) {
        throw new Error('Failed to fetch transactions');
    }
    return res.json();
}

/**
 * Create a new transaction via the API.
 * @param transaction Partial<Transaction> - New transaction data.
 */
export async function createTransaction(transaction: Partial<TransactionPost>): Promise<void> {
    const res = await fetch('/api/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transaction),
    });

    if (!res.ok) {
        throw new Error('Failed to create transaction');
    }
}
