import { ReviewByPRForm } from "@/components/review-by-pr-form";
import { ReviewByDiffForm } from "@/components/review-by-diff-form";
import { ReviewStatusChecker } from "@/components/review-status-checker";
import { Badge } from "@/components/ui/badge";
import { GitBranch, Shield, Zap, CheckCircle, Code, TrendingUp } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-12 md:py-20">
        <div className="max-w-6xl mx-auto space-y-16">
          <header className="text-center space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20">
              <GitBranch className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-primary">Automated Code Review</span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              GitHub PR Review Agent
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
              Production-ready automated code review agent that analyzes pull requests 
              and delivers human-quality, structured feedback with security, performance, 
              and style insights.
            </p>
          </header>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="flex flex-col items-center text-center p-6 rounded-lg bg-card border">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">Security Analysis</h3>
              <p className="text-sm text-muted-foreground">
                Detects SQL injection, XSS, and common vulnerabilities with Bandit & Semgrep
              </p>
            </div>

            <div className="flex flex-col items-center text-center p-6 rounded-lg bg-card border">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">Performance Review</h3>
              <p className="text-sm text-muted-foreground">
                Identifies O(n²) loops, inefficient patterns, and optimization opportunities
              </p>
            </div>

            <div className="flex flex-col items-center text-center p-6 rounded-lg bg-card border">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <CheckCircle className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">Multi-Agent System</h3>
              <p className="text-sm text-muted-foreground">
                10+ specialized agents analyze logic, readability, style, and test coverage
              </p>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            <ReviewByPRForm />
            <ReviewByDiffForm />
          </div>

          <div className="max-w-2xl mx-auto">
            <ReviewStatusChecker />
          </div>

          <div className="border-t pt-12">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold text-center mb-8">How It Works</h2>
              
              <div className="grid md:grid-cols-4 gap-6">
                <div className="text-center space-y-2">
                  <div className="h-10 w-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center mx-auto font-semibold">
                    1
                  </div>
                  <h4 className="font-medium">Submit PR</h4>
                  <p className="text-sm text-muted-foreground">
                    Provide GitHub repo & PR number or paste a diff
                  </p>
                </div>

                <div className="text-center space-y-2">
                  <div className="h-10 w-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center mx-auto font-semibold">
                    2
                  </div>
                  <h4 className="font-medium">Analysis</h4>
                  <p className="text-sm text-muted-foreground">
                    Multi-agent pipeline examines code changes
                  </p>
                </div>

                <div className="text-center space-y-2">
                  <div className="h-10 w-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center mx-auto font-semibold">
                    3
                  </div>
                  <h4 className="font-medium">Results</h4>
                  <p className="text-sm text-muted-foreground">
                    Structured JSON report with actionable feedback
                  </p>
                </div>

                <div className="text-center space-y-2">
                  <div className="h-10 w-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center mx-auto font-semibold">
                    4
                  </div>
                  <h4 className="font-medium">Optional Post</h4>
                  <p className="text-sm text-muted-foreground">
                    Automatically comment on GitHub PR
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-card border rounded-lg p-8 text-center space-y-4">
            <Code className="h-12 w-12 text-primary mx-auto" />
            <h3 className="text-xl font-semibold">Backend Architecture</h3>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Built with FastAPI, Celery, Redis, and PostgreSQL. Modular multi-agent system 
              with DiffParser, AST, StaticAnalysis, Security, Performance, Readability, Style, 
              TestCoverage, Summarizer, and CommentFormatter agents.
            </p>
            <div className="flex flex-wrap gap-2 justify-center pt-2">
              <Badge variant="secondary">Python 3.11+</Badge>
              <Badge variant="secondary">FastAPI</Badge>
              <Badge variant="secondary">LangChain</Badge>
              <Badge variant="secondary">PostgreSQL</Badge>
              <Badge variant="secondary">Docker</Badge>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}