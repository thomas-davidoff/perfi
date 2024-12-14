import TransactionsTable from "./transactionsTable";
import Accounts from "./accounts";

export default async function DashboardPage() {
    return (
        <div>
            <h1>Transactions</h1>
            <TransactionsTable />
            <Accounts />
        </div>
    );
}
