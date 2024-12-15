import {
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"

export default function FieldItem({ fieldName, children }: { fieldName: string, children: React.ReactNode }) {
    return (
        <FormItem>
            <div className="grid grid-cols-4 items-center gap-4 py-2">
                <FormLabel className="text-right">{fieldName}</FormLabel>
                <div className="col-span-3">
                    {children}
                </div>
                <FormMessage className="col-span-4 text-center"/>
            </div>
        </FormItem>
    )
}
