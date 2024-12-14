'use client';

import { useState } from 'react';
import { useAccounts } from '@/hooks/useAccounts';
import { useTransactions } from '@/hooks/useTransactions';
import { Button } from '@/components/ui/button';

export default function TransactionForm() {
    const { accounts, isLoading: accountsLoading } = useAccounts();
    const { addTransaction, loadTransactions } = useTransactions();

    const [formData, setFormData] = useState({
        description: '',
        amount: '',
        date: '',
        category: 'uncategorized',
        account_id: '',
        merchant: '',
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await addTransaction({
                description: formData.description,
                amount: parseFloat(formData.amount),
                date: formData.date,
                category: formData.category,
                merchant: formData.merchant,
                account_id: formData.account_id,
            });
            await loadTransactions();
            setFormData({
                description: '',
                amount: '',
                date: '',
                category: 'uncategorized',
                account_id: '',
                merchant: '',
            }); // Reset form
        } catch (error) {
            console.error('Error creating transaction:', error);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div>
                <label htmlFor="description">Description</label>
                <input
                    type="text"
                    id="description"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    className="input"
                />
            </div>
            <div>
                <label htmlFor="amount">Amount</label>
                <input
                    type="number"
                    id="amount"
                    name="amount"
                    value={formData.amount}
                    onChange={handleChange}
                    className="input"
                    required
                />
            </div>
            <div>
                <label htmlFor="date">Date</label>
                <input
                    type="date"
                    id="date"
                    name="date"
                    value={formData.date}
                    onChange={handleChange}
                    className="input"
                    required
                />
            </div>
            <div>
                <label htmlFor="merchant">Merchant</label>
                <input
                    type="text"
                    id="merchant"
                    name="merchant"
                    value={formData.merchant}
                    onChange={handleChange}
                    className="input"
                    required
                />
            </div>
            <div>
                <label htmlFor="category">Category</label>
                <input
                    type="text"
                    id="category"
                    name="category"
                    value={formData.category}
                    onChange={handleChange}
                    className="input"
                />
            </div>
            <div>
                <label htmlFor="account_id">Account</label>
                {accountsLoading ? (
                    <p>Loading accounts...</p>
                ) : (
                    <select
                        id="account_id"
                        name="account_id"
                        value={formData.account_id}
                        onChange={handleChange}
                        className="input"
                        required
                    >
                        <option value="">Select an account</option>
                        {accounts.map((account) => (
                            <option key={account.id} value={account.id}>
                                {account.name}
                            </option>
                        ))}
                    </select>
                )}
            </div>
            <Button type="submit" variant="outline">
                Create Transaction
            </Button>
        </form>
    );
}
