import { getTransactions } from "@/lib/getTransactions";


export default async function DashboardPage() {

    const data = await getTransactions()

    return (
        <div>
            <h1>Transactions</h1>
            <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
    );
}
