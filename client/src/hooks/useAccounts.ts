import { useEffect, useState } from 'react';
import { Account } from '@/types';
import { fetchAccounts } from '@/lib/accounts/accounts';

export function useAccounts() {
    const [accounts, setAccounts] = useState<Account[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const loadAccounts = async () => {
        setIsLoading(true);
        try {
            const data = await fetchAccounts();
            setAccounts(data);
        } catch (error) {
            console.error('Error fetching accounts:', error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadAccounts();
    }, []);

    return { accounts, isLoading, loadAccounts };
}
