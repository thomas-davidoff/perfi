'use client'

import React, { useState } from "react";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { MoreHorizontal } from "lucide-react";
import { TransactionDetailsSheet } from "./transctions-details-sheet";
import { Transaction } from "@/types";

export function TransactionActionsDropdown({ transaction }: { transaction: Transaction }) {
    const [isSheetOpen, setIsSheetOpen] = useState(false);
    const [dropdownOpen, setDropdownOpen] = useState(false);

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
                    <DropdownMenuItem>
                        Update transaction
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => console.log("Delete transaction")}>
                        Delete transaction
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>

            {/* Pass state to the Sheet */}
            <TransactionDetailsSheet isOpen={isSheetOpen} onClose={() => { setIsSheetOpen(false) }} />
        </>
    );
}
