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


export interface ListTransactionsResponse {
    data: Transaction[]
}


export interface Account extends FullRecordResponse {
    account_type: string,
    balance: number,
    name: string,
    user_id: User
}

export interface ListAccountsResponse {
    data: Account[]
}

export interface User extends FullRecordResponse {
    username: string,
    email: string
}

export interface Record {
    id: string
}

interface FullRecordResponse extends Record {
    created_at: string,
    updated_at: string
}


export interface TransactionPost {
    account_id: string,
    amount: number,
    date: Date,
    merchant: string,
    category: string,
    description: string
}
