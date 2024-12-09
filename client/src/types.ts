// src/types.ts
export interface Transaction {
    account: AccountCompact,
    amount: number,
    category: string,
    created_at: string,
    date: string,
    description: string,
    id: string,
    merchant: string,
    updated_at: string
}

export interface AccountCompact {
    account_type: string,
    id: string,
    name: string
}
