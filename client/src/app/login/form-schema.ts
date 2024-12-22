
import { z } from "zod"
export default z.object({
    username: z.string(),
    password: z.string()
});
