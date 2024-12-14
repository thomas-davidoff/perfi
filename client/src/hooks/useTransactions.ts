import { useEffect, useState } from 'react';
import { Transaction } from '@/types';
import { fetchTransactions, createTransaction } from '@/lib/transactions/fetchTransactions';

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

    const addTransaction = async (transaction: Partial<Transaction>) => {
        try {
            await createTransaction(transaction);
            await loadTransactions();
        } catch (error) {
            console.error('Error creating transaction:', error);
        }
    };

    useEffect(() => {
        loadTransactions();
    }, []);

    return { transactions, isLoading, loadTransactions, addTransaction };
}
