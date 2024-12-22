'use client'

import React, { useState } from "react";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { MoreHorizontal } from "lucide-react";
import { TransactionDetailsSheet } from "./transctions-details-sheet";
import { Transaction } from "@/types";
import { useTransactionsContext } from "@/context/TransactionsContext";

export function TransactionActionsDropdown({ transaction }: { transaction: Transaction }) {
    const [isSheetOpen, setIsSheetOpen] = useState(false);
    const [dropdownOpen, setDropdownOpen] = useState(false);

    const { deleteTransaction } = useTransactionsContext();

    const handleDelete = (id: string) => {
        if (confirm('Are you sure you want to delete this transaction?')) {
            deleteTransaction(id);
        }
    }

    return (
        <>
            <DropdownMenu open={dropdownOpen} onOpenChange={(isOpen) => {
                setDropdownOpen(isOpen)
            }}>
                <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Open menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => navigator.clipboard.writeText(transaction.id)}>
                        Copy transaction ID
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => {
                        setDropdownOpen(false) // super important: https://github.com/shadcn-ui/ui/issues/1859#issuecomment-2434816790
                        setIsSheetOpen(true)
                    }}>
                        View Details
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    {/* <DropdownMenuItem>
                        Update transaction
                    </DropdownMenuItem> */}
                    {/* todo ^ */}
                    <DropdownMenuItem onClick={() => handleDelete(transaction.id)}>
                        Delete transaction
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>

            {/* Pass state to the Sheet */}
            <TransactionDetailsSheet isOpen={isSheetOpen} onClose={() => { setIsSheetOpen(false) }} transaction={transaction}/>
        </>
    );
}
