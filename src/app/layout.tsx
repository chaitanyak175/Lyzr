import type { Metadata } from "next";
import "./globals.css";
import VisualEditsMessenger from "../visual-edits/VisualEditsMessenger";
import ErrorReporter from "@/components/ErrorReporter";
import Script from "next/script";
import { Toaster } from "@/components/ui/sonner";

export const metadata: Metadata = {
  title: "GitHub PR Review Agent | Automated Code Review",
  description: "Production-ready automated code review agent that analyzes pull requests and delivers human-quality, structured feedback with security, performance, and style insights.",
  icons: {
    icon: "https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/project-uploads/135098ff-1769-4205-bbf9-c020f9ee8fa5/generated_images/modern-minimalist-favicon-icon-for-githu-ea4a5f1e-20251123134152.jpg",
    shortcut: "https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/project-uploads/135098ff-1769-4205-bbf9-c020f9ee8fa5/generated_images/modern-minimalist-favicon-icon-for-githu-ea4a5f1e-20251123134152.jpg",
    apple: "https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/project-uploads/135098ff-1769-4205-bbf9-c020f9ee8fa5/generated_images/modern-minimalist-favicon-icon-for-githu-ea4a5f1e-20251123134152.jpg",
  },
  openGraph: {
    title: "GitHub PR Review Agent",
    description: "Automated code review with multi-agent analysis",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <ErrorReporter />
        <Script
          src="https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/scripts//route-messenger.js"
          strategy="afterInteractive"
          data-target-origin="*"
          data-message-type="ROUTE_CHANGE"
          data-include-search-params="true"
          data-only-in-iframe="true"
          data-debug="true"
          data-custom-data='{"appName": "YourApp", "version": "1.0.0", "greeting": "hi"}'
        />
        {children}
        <Toaster />
        <VisualEditsMessenger />
      </body>
    </html>
  );
}