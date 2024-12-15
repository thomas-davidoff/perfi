import { Checkbox } from "@/components/ui/checkbox"
import { Transaction } from "@/types"
import { ColumnDef } from "@tanstack/react-table"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

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
    },
    {
        id: "actions",
        cell: ({ row }) => {
          const transaction = row.original

          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                  <span className="sr-only">Open menu</span>
                  <p>Some icon: todo</p>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                <DropdownMenuItem
                  onClick={() => navigator.clipboard.writeText(transaction.id)}
                >
                  Copy transaction ID
                </DropdownMenuItem>
                {/* todo: view details popover */}
                <DropdownMenuItem>View details</DropdownMenuItem>
                <DropdownMenuSeparator />
                {/* todo: update handler */}
                <DropdownMenuItem>Update transaction</DropdownMenuItem>
                {/* todo: delete handler */}
                <DropdownMenuItem>Delete transaction</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )
        },
      },
]
