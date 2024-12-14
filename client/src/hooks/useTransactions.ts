import { useEffect, useState } from 'react';
import { Transaction, TransactionPost } from '@/types';
import { fetchTransactions, createTransaction } from '@/lib/fetch/transactions';

export function useTransactions() {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const loadTransactions = async () => {
        setIsLoading(true);
        try {
            const data = await fetchTransactions();
            setTransactions(data);
        } catch (error) {
            console.error('Error fetching transactions:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const addTransaction = async (transaction: Partial<TransactionPost>) => {
        try {
            await createTransaction(transaction);
            await loadTransactions();
        } catch (error: any) {
            console.error('Error creating transaction:', error.message);
            alert(`Error: ${error.message}`);
        }
    };

    useEffect(() => {
        loadTransactions();
    }, []);

    return { transactions, isLoading, loadTransactions, addTransaction };
}
