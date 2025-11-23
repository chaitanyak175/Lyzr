"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, Loader2, CheckCircle, AlertCircle, Clock } from "lucide-react";
import { toast } from "sonner";

export function ReviewStatusChecker() {
  const [loading, setLoading] = useState(false);
  const [runId, setRunId] = useState("");
  const [result, setResult] = useState<any>(null);

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/review/${runId}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch review: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
      toast.success("Review status retrieved successfully");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to fetch review status");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed":
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500/10 text-green-500 border-green-500/20";
      case "failed":
        return "bg-destructive/10 text-destructive border-destructive/20";
      default:
        return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Search className="h-5 w-5 text-primary" />
          <CardTitle>Check Review Status</CardTitle>
        </div>
        <CardDescription>
          Enter a run ID to view review results
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleCheck} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="run-id">Run ID</Label>
            <div className="flex gap-2">
              <Input
                id="run-id"
                placeholder="e.g., 7a8b9c0d"
                value={runId}
                onChange={(e) => setRunId(e.target.value)}
                required
              />
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  "Check"
                )}
              </Button>
            </div>
          </div>

          {result && (
            <div className="mt-4 space-y-3 pt-3 border-t">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Status</span>
                <Badge variant="outline" className={getStatusColor(result.status)}>
                  <span className="flex items-center gap-1.5">
                    {getStatusIcon(result.status)}
                    {result.status}
                  </span>
                </Badge>
              </div>

              {result.summary && (
                <div className="space-y-1">
                  <span className="text-sm font-medium">Summary</span>
                  <p className="text-sm text-muted-foreground">{result.summary}</p>
                </div>
              )}

              {result.file_reviews && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Issues Found</span>
                  <span className="font-medium">
                    {result.file_reviews.reduce((acc: number, file: any) => 
                      acc + (file.issues?.length || 0), 0
                    )}
                  </span>
                </div>
              )}

              {result.meta?.duration_seconds && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Duration</span>
                  <span className="font-medium">{result.meta.duration_seconds}s</span>
                </div>
              )}

              <Button 
                variant="outline" 
                className="w-full mt-2"
                onClick={() => {
                  const jsonStr = JSON.stringify(result, null, 2);
                  const blob = new Blob([jsonStr], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `review-${result.run_id}.json`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
              >
                Download Detailed Report
              </Button>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  );
}