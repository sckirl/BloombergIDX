import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IDX OpenInsider - Institutional Intelligence",
  description: "Bloomberg-tier Indonesian insider trading intelligence platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-bg text-fg font-mono">
        {children}
      </body>
    </html>
  );
}
