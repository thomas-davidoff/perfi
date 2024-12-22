import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Personal Finance",
  description: "Central management of personal finances",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
