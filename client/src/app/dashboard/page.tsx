import { TransactionsProvider } from "@/context/TransactionsContext";
import TransactionsTable from "./transactions-table";
import { TransactionForm } from "./transactions-form";

export default async function DashboardPage() {
    return (
        <div>
            <TransactionsProvider>
                <TransactionForm />
                <TransactionsTable />
            </TransactionsProvider>
        </div>
    );
}
