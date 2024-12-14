import TransactionsTable from "./transactionsTable";
import TransactionForm from "./transactionForm";

export default async function DashboardPage() {
    return (
        <div>
            <h1>Transactions</h1>
            <TransactionsTable />
            <TransactionForm />
        </div>
    );
}
