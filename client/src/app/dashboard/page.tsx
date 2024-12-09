import { getTransactions } from "@/lib/getTransactions";
import { columns } from "@/app/dashboard/columns";
import { DataTable } from "@/components/ui/data-table";
import { Button } from "@/components/ui/button"

export default async function DashboardPage() {
    const data = await getTransactions()
    return (
        <div>
            <h1>Transactions</h1>
            <Button variant="outline">Create Transaction</Button>
            <Button variant="outline">Delete Transaction</Button>
            <DataTable columns={columns} data={data} />
        </div>
    );
}
