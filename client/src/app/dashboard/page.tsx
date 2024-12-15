import TransactionForm from "./transactionForm";
import { TransactionsProvider } from "@/context/TransactionsContext";
import TransactionsTable from "./transactions-table";

export default async function DashboardPage() {
    return (
        <div>
            <TransactionsProvider>
                <TransactionsTable />
                <TransactionForm />
            </TransactionsProvider>
        </div>
    );
}
