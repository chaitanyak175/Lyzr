"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { FileText, Loader2 } from "lucide-react";
import { toast } from "sonner";

export function ReviewByDiffForm() {
  const [loading, setLoading] = useState(false);
  const [diffText, setDiffText] = useState("");
  const [runLinters, setRunLinters] = useState(true);
  const [runSecurity, setRunSecurity] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/review/diff`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          diff_text: diffText,
          repo_full_name: null,
          run_options: {
            run_linters: runLinters,
            run_security_scan: runSecurity,
            post_to_github: false,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to submit review: ${response.statusText}`);
      }

      const data = await response.json();
      toast.success(`Review queued successfully! Run ID: ${data.run_id}`);
      
      setDiffText("");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to submit review");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary" />
          <CardTitle>Review by Diff</CardTitle>
        </div>
        <CardDescription>
          Paste a unified diff for analysis
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="diff-text">Diff Content</Label>
            <Textarea
              id="diff-text"
              placeholder="diff --git a/src/app.py b/src/app.py&#10;index 1234567..abcdefg 100644&#10;--- a/src/app.py&#10;+++ b/src/app.py&#10;@@ -1,3 +1,4 @@&#10;+import os&#10; def main():&#10;     pass"
              value={diffText}
              onChange={(e) => setDiffText(e.target.value)}
              className="font-mono text-sm min-h-[300px]"
              required
            />
          </div>

          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="diff-run-linters" className="text-sm font-normal">
                Run Linters
              </Label>
              <Switch
                id="diff-run-linters"
                checked={runLinters}
                onCheckedChange={setRunLinters}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <Label htmlFor="diff-run-security" className="text-sm font-normal">
                Run Security Scan
              </Label>
              <Switch
                id="diff-run-security"
                checked={runSecurity}
                onCheckedChange={setRunSecurity}
              />
            </div>
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              "Analyze Diff"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}