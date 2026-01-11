import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Novel to Kids Illustration",
  description: "Convert novels into illustrations for kids",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-blue-50">
        {children}
      </body>
    </html>
  );
}
