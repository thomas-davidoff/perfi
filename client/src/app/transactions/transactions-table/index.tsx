'use client'

import { Checkbox } from "@/components/ui/checkbox"
import { Transaction } from "@/types"
import { ColumnDef } from "@tanstack/react-table"
import { Button } from "@/components/ui/button"
import { ArrowUpDown } from "lucide-react"
import { useTransactionsContext } from "@/context/TransactionsContext";
import { DataTable } from "@/components/ui/record-table";
import { useState } from "react"
import { CreateTransactionForm } from "../create-transaction-form"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { CirclePlus } from "lucide-react"
import { useAccounts } from "@/hooks/useAccounts"
import { TransactionActionsDropdown } from "./transaction-row-actions"

export function TransactionsTable() {

    const { accounts } = useAccounts()
    const [selectedRows, setSelectedRows] = useState({})
    const { transactions } = useTransactionsContext();

    const { deleteTransaction } = useTransactionsContext();

    const handleDelete = (id: string) => {
        if (confirm('Are you sure you want to delete this transaction?')) {
            deleteTransaction(id);
        }
    }

    const handleDeleteSelected = async () => {
        const selectedTransactionIds = Object.keys(selectedRows)
            .filter((key) => selectedRows[key])
            .map((key) => transactions[parseInt(key)].id);

        if (
            selectedTransactionIds.length &&
            confirm(
                `Are you sure you want to delete ${selectedTransactionIds.length} transaction(s)?`
            )
        ) {
            selectedTransactionIds.forEach((id) => deleteTransaction(id));
            setSelectedRows({});
        }
    };

    const columns: ColumnDef<Transaction>[] = [
        {
            id: "select",
            header: ({ table }) => (
                <Checkbox
                    checked={
                        table.getIsAllPageRowsSelected() ||
                        (table.getIsSomePageRowsSelected() && "indeterminate")
                    }
                    onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
                    aria-label="Select all"
                />
            ),
            cell: ({ row }) => (
                <Checkbox
                    checked={row.getIsSelected()}
                    onCheckedChange={(value) => row.toggleSelected(!!value)}
                    aria-label="Select row"
                />
            ),
        },
        {
            accessorKey: "id",
            header: "Id"
        },
        {
            accessorKey: "date",
            header: ({ column }) => {
                return (
                    <Button
                        variant="ghost"
                        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
                    >
                        Date
                        <ArrowUpDown className="ml-2 h-4 w-4" />
                    </Button>
                )
            },
            sortingFn: (rowA, rowB) => {
                const dateA = new Date(rowA.getValue<string>('date'));
                const dateB = new Date(rowB.getValue<string>('date'));
                return dateA.getTime() - dateB.getTime();
            },
        },
        {
            accessorKey: "merchant",
            header: "Merchant"
        },
        {
            accessorKey: "amount",
            header: "Amount",
        },
        {
            accessorKey: "category",
            header: "Category",
        },
        {
            accessorKey: "account.name",
            header: "Account",
        },
        {
            id: "actions",
            cell: ({ row }) => {
                return <TransactionActionsDropdown transaction={row.original} />
            },
        },
    ]

    return (
        <div>
            <div className="flex py-4 justify-between">
                <Dialog>
                    <DialogTrigger asChild>
                        <Button variant='outline'>
                            <CirclePlus /> Create Transaction
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[425px]">
                        <DialogHeader>
                            <DialogTitle>Create a transaction</DialogTitle>
                            <DialogDescription>
                                Create a new transaction. Click save when you&apos;re done.
                            </DialogDescription>
                        </DialogHeader>
                        <CreateTransactionForm accounts={accounts} formId="create-transactions-form" />
                        <DialogFooter>
                            <Button type="submit" form="create-transactions-form">Submit</Button>
                        </DialogFooter>
                    </DialogContent>

                </Dialog>

                <Button variant='outline' onClick={handleDeleteSelected} disabled={Object.keys(selectedRows).length === 0}>
                    Delete transaction(s)
                </Button>
            </div>
            <DataTable columns={columns} data={transactions} rowSelection={selectedRows} setRowSelection={setSelectedRows} />
        </div>
    )
}
