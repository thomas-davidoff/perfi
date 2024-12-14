'use client';

import { useEffect, useState } from 'react';
import { fetchTransactions, createTransaction } from '@/lib/transactions/fetchTransactions';
import { columns } from '@/app/dashboard/columns';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { Transaction } from '@/types';

export default function TransactionsTable() {
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

    const handleCreateTransaction = async () => {
        try {
            await createTransaction({
                description: 'Test',
                amount: 100,
                date: new Date().toISOString(),
                category: 'uncategorized',
                merchant: "Some merchant",
                // account_id: "uuid" // TODO: This won't work until implement get account ids
            });
            await loadTransactions(); // Refresh the data
        } catch (error) {
            console.error('Error creating transaction:', error);
        }
    };

    useEffect(() => {
        loadTransactions();
    }, []);

    return (
        <div>
            <div className="flex space-x-2">
                <Button variant="outline" onClick={handleCreateTransaction}>
                    Create Transaction
                </Button>
                <Button variant="outline" onClick={loadTransactions}>
                    Refresh
                </Button>
            </div>
            {isLoading ? (
                <p>Loading...</p>
            ) : (
                <DataTable columns={columns} data={transactions} />
            )}
        </div>
    );
}
