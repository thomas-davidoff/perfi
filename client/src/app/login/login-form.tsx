'use client'

import schema from './form-schema'
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import {
    Form,
    FormField,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { z } from "zod"
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { signIn } from 'next-auth/react';
import { useRouter, useSearchParams } from 'next/navigation'
import { toast } from "sonner"

export function LoginForm() {

    const router = useRouter()
    const searchParams = useSearchParams()
    const redirectTo = searchParams.get('callbackUrl') || '/transactions'

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
            router.push(redirectTo)
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
            <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
                <div className='rounded-md space-y-4'>
                    <FormField
                        control={form.control}
                        name="username"
                        render={({ field }) => (
                            <div>
                                <FormLabel className="text-right">Username</FormLabel>
                                <Input placeholder="username" {...field} />
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
                <div className='flex justify-end'>
                <Button type="submit" >Submit</Button>
                </div>

            </form>
        </Form>
    )
}
