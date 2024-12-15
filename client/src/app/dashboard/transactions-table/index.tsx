'use client'

import { useTransactionsContext } from "@/context/TransactionsContext";
import { DataTable } from "@/components/ui/record-table";
import { columns } from "./columns";

export default function TransactionsTable() {
    const { transactions } = useTransactionsContext();

    return (
        <DataTable columns={columns} data={transactions} />
    )

}
