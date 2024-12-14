export interface AccountCompact extends Record {
    account_type: string,
    name: string
}

export interface Transaction extends FullRecordResponse {
    account: AccountCompact,
    amount: number,
    category: string,
    date: string,
    description: string,
    merchant: string,
}

export interface Account extends FullRecordResponse {
    account_type: string,
    balance: number,
    name: string,
    user_id: User
}

export interface User extends FullRecordResponse {
    username: string,
    email: string
}

interface Record {
    id: string
}

interface FullRecordResponse extends Record {
    created_at: string,
    updated_at: string
}
