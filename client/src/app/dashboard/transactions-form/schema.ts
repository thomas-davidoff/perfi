
import { z } from "zod"
export default z.object({

    merchant: z.string().min(1, {
        message: "Merchant cannot be blank.",
    }),
    description: z.string().optional(),
    amount: z
        .number()
        .min(-10000).max(10000),
    date: z.coerce.date(),
    category: z.string(),
    account_id: z.string(),
});
