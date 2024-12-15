'use client';

import React, { createContext, useContext } from 'react';
import { useTransactions } from '@/hooks/useTransactions';

interface TransactionsContextProps {
    transactions: ReturnType<typeof useTransactions>['transactions'];
    isLoading: ReturnType<typeof useTransactions>['isLoading'];
    loadTransactions: ReturnType<typeof useTransactions>['loadTransactions'];
    addTransaction: ReturnType<typeof useTransactions>['addTransaction'];
    deleteTransaction: ReturnType<typeof useTransactions>['deleteTransaction'];
}

const TransactionsContext = createContext<TransactionsContextProps | undefined>(undefined);

export const TransactionsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { transactions, isLoading, loadTransactions, addTransaction, deleteTransaction } = useTransactions();

    return (
        <TransactionsContext.Provider value={{ transactions, isLoading, loadTransactions, addTransaction, deleteTransaction }}>
            {children}
        </TransactionsContext.Provider>
    );
};

export const useTransactionsContext = () => {
    const context = useContext(TransactionsContext);
    if (!context) {
        throw new Error('useTransactionsContext must be used within a TransactionsProvider');
    }
    return context;
};
