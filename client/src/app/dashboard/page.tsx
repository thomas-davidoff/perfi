import { getTransactions } from "@/lib/getTransactions";
import { redirectToLogin } from "@/lib/redirectToLogin";


export default async function DashboardPage() {

    await redirectToLogin()

    const data = await getTransactions()

    return (
        <div>
            <h1>Transactions</h1>
            <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
    );
}
