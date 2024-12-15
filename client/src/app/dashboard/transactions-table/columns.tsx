import { Checkbox } from "@/components/ui/checkbox"
import { Transaction } from "@/types"
import { ColumnDef } from "@tanstack/react-table"

export const columns: ColumnDef<Transaction>[] = [
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
