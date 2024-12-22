'use client'

import schema from './form-schema'
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
    FormDescription
} from "@/components/ui/form"
import { z } from "zod"
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation'
import { toast } from "sonner"

export function LoginForm() {

    const router = useRouter()

    const form = useForm<z.infer<typeof schema>>({
        resolver: zodResolver(schema),
        defaultValues: {
            username: "",
            password: ""
        },
    });

    async function handleSubmit(values: z.infer<typeof schema>) {
        console.log(values)
        const res = await signIn('credentials', {
            username: values.username,
            password: values.password,
            redirect: false
        })

        if (res?.status === 200) {
            router.push('/transactions')
            return
        }

        if (res?.status === 401 && res.error) {

            toast.error("Error", {
                description: res.error,
            })

        } else {
            toast.error("An unexpected error occurred.")
            console.error('An unexpected error occurred.')
        }
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(handleSubmit)}>
                <div>
                    <FormField
                        control={form.control}
                        name="username"
                        render={({ field }) => (
                            <div>
                                <FormLabel className="text-right">Username</FormLabel>
                                <Input placeholder="username" {...field} />
                                <FormDescription>
                                    This is your username or email.
                                </FormDescription>
                                <FormMessage />
                            </div>

                        )}
                    />
                    <FormField
                        control={form.control}
                        name="password"
                        render={({ field }) => (
                            <div>
                                <FormLabel className="text-right">Password</FormLabel>
                                <Input placeholder="password" {...field} type='password' />
                                <FormMessage />
                            </div>

                        )}
                    />
                </div>
                <Button type="submit">Submit</Button>
            </form>
        </Form>
    )
}
