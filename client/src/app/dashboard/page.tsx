import TransactionsTable from "./transactionsTable";

export default async function DashboardPage() {
    return (
        <div>
            <h1>Transactions</h1>
            <TransactionsTable />
        </div>
    );
}
