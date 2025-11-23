"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { GitPullRequest, Loader2 } from "lucide-react";
import { toast } from "sonner";

export function ReviewByPRForm() {
  const [loading, setLoading] = useState(false);
  const [repoName, setRepoName] = useState("");
  const [prNumber, setPrNumber] = useState("");
  const [githubToken, setGithubToken] = useState("");
  const [runLinters, setRunLinters] = useState(true);
  const [runSecurity, setRunSecurity] = useState(true);
  const [postToGithub, setPostToGithub] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/review/pr`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_full_name: repoName,
          pr_number: parseInt(prNumber),
          github_token: githubToken || undefined,
          run_options: {
            run_linters: runLinters,
            run_security_scan: runSecurity,
            post_to_github: postToGithub,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to submit review: ${response.statusText}`);
      }

      const data = await response.json();
      toast.success(`Review queued successfully! Run ID: ${data.run_id}`);
      
      setRepoName("");
      setPrNumber("");
      setGithubToken("");
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
          <GitPullRequest className="h-5 w-5 text-primary" />
          <CardTitle>Review by Pull Request</CardTitle>
        </div>
        <CardDescription>
          Analyze a GitHub PR by repository and PR number
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="repo-name">Repository (owner/repo)</Label>
            <Input
              id="repo-name"
              placeholder="octocat/Hello-World"
              value={repoName}
              onChange={(e) => setRepoName(e.target.value)}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="pr-number">PR Number</Label>
            <Input
              id="pr-number"
              type="number"
              placeholder="123"
              value={prNumber}
              onChange={(e) => setPrNumber(e.target.value)}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="github-token">GitHub Token (optional)</Label>
            <Input
              id="github-token"
              type="password"
              placeholder="ghp_xxxxxxxxxxxx"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Leave empty to use server token. Provide your own for private repos or to post comments.
            </p>
          </div>

          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="run-linters" className="text-sm font-normal">
                Run Linters
              </Label>
              <Switch
                id="run-linters"
                checked={runLinters}
                onCheckedChange={setRunLinters}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <Label htmlFor="run-security" className="text-sm font-normal">
                Run Security Scan
              </Label>
              <Switch
                id="run-security"
                checked={runSecurity}
                onCheckedChange={setRunSecurity}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <Label htmlFor="post-to-github" className="text-sm font-normal">
                Post to GitHub
              </Label>
              <Switch
                id="post-to-github"
                checked={postToGithub}
                onCheckedChange={setPostToGithub}
              />
            </div>
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submitting...
              </>
            ) : (
              "Start Review"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}