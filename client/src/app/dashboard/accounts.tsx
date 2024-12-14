'use client';

import { useAccounts } from "@/hooks/useAccounts"


export default function Accounts() {

    const { accounts, isLoading } = useAccounts()

    return (
        <div>
            <h1>Accounts</h1>
            {isLoading ? (
                <p>Loading...</p>
            ) : (
                <p>
                    {JSON.stringify(accounts)}
                </p>
            )}
        </div>
    )
}
