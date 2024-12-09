
"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Transaction } from "@/types"

export const columns: ColumnDef<Transaction>[] = [
    {
        accessorKey: "date",
        header: "Date"
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
    }
]
