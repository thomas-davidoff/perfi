'use client'

import React from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter, SheetClose } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Transaction } from "@/types";


const Row = ({ name, val }: { name: string, val: string }) => {
    return (
        <>
            <div className="col-span-1">
                <b>{name}</b>
            </div>
            <div className="col-span-3">
                {val}
            </div>
        </>
    )
}

export function TransactionDetailsSheet({ isOpen, onClose, transaction }: { isOpen: boolean, onClose: () => void, transaction: Transaction }) {
    return (
        <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <SheetContent side="right">
                <SheetHeader>
                    <SheetTitle>Transaction Details</SheetTitle>
                    <SheetDescription>
                        id: {transaction.id}
                    </SheetDescription>
                </SheetHeader>
                <div className="grid gap-4 py-2 grid-cols-4">
                    <Row name="Date" val={transaction.date} />
                    <Row name="Merchant" val={transaction.merchant} />
                    <Row name="Amount" val={transaction.amount.toString()} />
                    <Row name="Category" val={transaction.category} />
                    <Row name="Description" val={transaction.description} />
                    <Row name="Account" val={transaction.account.name} />
                </div>
                <SheetFooter>
                    {/* This button will trigger the close */}
                    <SheetClose asChild>
                        <Button>Close</Button>
                    </SheetClose>
                </SheetFooter>
            </SheetContent>
        </Sheet>
    );
}
