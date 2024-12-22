'use client'

import React from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter, SheetClose } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";

export function TransactionDetailsSheet({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
    return (
        <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <SheetContent side="right">
                <SheetHeader>
                    <SheetTitle>Transaction Details</SheetTitle>
                    <SheetDescription>
                        View or edit transaction details.
                    </SheetDescription>
                </SheetHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <label htmlFor="name" className="text-right">
                            Name
                        </label>
                        <input id="name" defaultValue="Transaction Name" className="input" />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <label htmlFor="amount" className="text-right">
                            Amount
                        </label>
                        <input id="amount" defaultValue="$100" className="input" />
                    </div>
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
