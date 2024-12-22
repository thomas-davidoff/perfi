import "./globals.css";
import type { Metadata } from "next";
import { Toaster } from "@/components/ui/sonner"

export const metadata: Metadata = {
  title: "Personal Finance",
  description: "Central management of personal finances",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">
        <main>{children}</main>
        <Toaster />
      </body>
    </html>
  );
}
