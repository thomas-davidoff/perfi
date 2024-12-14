export interface AccountCompact {
    account_type: string,
    id: string,
    name: string
}

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

export interface Account {
    account_type: string,
    balance: number,
    created_at: string,
    id: string,
    name: string,
    updated_at: string,
    user_id: User
}

export interface User {
    id: string,
    updated_at: string,
    username: string,
    created_at: string,
    email: string
}
