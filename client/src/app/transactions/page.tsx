import { TransactionsProvider } from "@/context/TransactionsContext";
import { TransactionsTable } from "./transactions-table";


export default async function DashboardPage() {
    return (
        <div className="p-5">
            <TransactionsProvider>
                <TransactionsTable />
            </TransactionsProvider>
        </div>
    );
}
