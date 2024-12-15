import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"


// requirements
// step-based approach:
// - upload file
// - select headers and what not
// checkbox to "allow" or "disallow" duplicate records (like same transactions)
// assign to a particular account, or require an "account" header
// preview (does this look correct?)

export default function ImportPage() {
    return (
        <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="transactions">File</Label>
            <Input id="transactions" type="file" />
        </div>
    )
}
