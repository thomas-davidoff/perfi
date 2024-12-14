import TransactionsTable from "./transactionsTable";
import TransactionForm from "./transactionForm";
import { TransactionsProvider } from "@/context/TransactionsContext";

export default async function DashboardPage() {
    return (
        <div>
            <h1>Transactions</h1>
            <TransactionsProvider>
                <TransactionsTable />
                <TransactionForm />
            </TransactionsProvider>
        </div>
    );
}
