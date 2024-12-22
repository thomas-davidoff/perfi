"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
} from "@/components/ui/form"
import {
  cn
} from "@/lib/utils"
import { Input } from "@/components/ui/input"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import {
  Calendar
} from "@/components/ui/calendar"
import {
  Calendar as CalendarIcon
} from "lucide-react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select"
import { useTransactionsContext } from "@/context/TransactionsContext";
import formSchema from './schema'
import FieldItem from "./field-item"
import { Account } from "@/types"


export function CreateTransactionForm({ accounts, formId }: { accounts: Account[], formId: string }) {

  const { addTransaction } = useTransactionsContext();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      merchant: "",
      amount: 0,
      category: "",
      date: new Date(),
      account_id: "",
      description: "",
    },
  })

  async function onSubmit(values: z.infer<typeof formSchema>) {
    console.log("Values from form:")
    console.log(values)
    try {
      const res = await addTransaction(values);
    } catch (err: any) {
      console.log(err)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} id={formId}>
        <div className="grid gap-y-0">
          <FormField
            control={form.control}
            name="merchant"
            render={({ field }) => (
              <FieldItem fieldName="Merchant">
                <Input placeholder="Trader Joes" {...field} />
              </FieldItem>

            )}
          />
          <FormField
            name="amount"
            control={form.control}
            render={({ field }) => (
              <FieldItem fieldName="Amount">
                <Input
                  type="number"
                  placeholder="Enter amount"
                  {...field}
                  step="1"
                  onChange={event => field.onChange(+event.target.value)}
                />
              </FieldItem>

            )}
          />
          <FormField
            control={form.control}
            name="date"
            render={({ field }) => (
              <FieldItem fieldName="Date">
                <Popover>
                  <PopoverTrigger asChild>
                    <FormControl>
                      <Button
                        variant={"outline"}
                        className={cn(
                          "w-[100%] pl-3 text-left font-normal",
                          !field.value && "text-muted-foreground"
                        )}
                      >
                        {field.value ? (
                          field.value.toISOString().split('T')[0]
                        ) : (
                          <span>Pick a date</span>
                        )}
                        <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                      </Button>
                    </FormControl>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                      mode="single"
                      selected={field.value}
                      onSelect={field.onChange}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </FieldItem>
            )}
          />
          <FormField
            control={form.control}
            name="category"
            render={({ field }) => (
              <FieldItem fieldName="Category">
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a category" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="uncategorized">Uncategorized</SelectItem>
                  </SelectContent>
                </Select>
              </FieldItem>
            )}
          />
          <FormField
            control={form.control}
            name="account_id"
            render={({ field }) => (
              <FieldItem fieldName="Account">
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder={accounts[0].name} defaultValue={accounts[0].id} />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {accounts.map(acc => (
                      <SelectItem value={acc.id} key={`${acc.name}_item`}>{acc.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FieldItem>
            )}
          />
          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FieldItem fieldName="Description">
                <FormControl>
                  <Input placeholder="Some description..." {...field} />
                </FormControl>
              </FieldItem>
            )}
          />
        </div>
      </form>
    </Form>

  )
}
