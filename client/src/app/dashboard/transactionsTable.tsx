'use client';

import { columns } from '@/app/dashboard/columns';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { useTransactions } from '@/hooks/useTransactions';

export default function TransactionsTable() {
    const { transactions, isLoading, loadTransactions } = useTransactions();

    return (
        <div>
            <div className="flex space-x-2">
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
