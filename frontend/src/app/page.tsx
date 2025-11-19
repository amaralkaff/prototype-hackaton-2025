import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4">
            Amarta AI
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Multimodal AI-powered credit scoring system for micro-entrepreneurs
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle>Borrowers</CardTitle>
              <CardDescription>
                View and manage borrower profiles, track business information and financial history
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/borrowers">
                <Button className="w-full">View Borrowers</Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle>Loans</CardTitle>
              <CardDescription>
                Monitor loan portfolio, track repayments and analyze financial performance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/loans">
                <Button className="w-full">View Loans</Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow border-2 border-blue-200 bg-blue-50/50">
            <CardHeader>
              <CardTitle className="text-blue-900">Credit Assessment</CardTitle>
              <CardDescription className="text-blue-700">
                AI-powered multimodal credit scoring with income validation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/credit-assessment">
                <Button className="w-full bg-blue-600 hover:bg-blue-700">Run Assessment</Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle>Analytics</CardTitle>
              <CardDescription>
                Portfolio statistics, risk distribution and performance metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/analytics">
                <Button className="w-full">View Analytics</Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        <div className="mt-16 text-center">
          <h2 className="text-2xl font-semibold mb-4">Key Features</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto mt-8">
            <div className="p-6 rounded-lg bg-card">
              <h3 className="font-semibold mb-2">📊 ML Scoring</h3>
              <p className="text-sm text-muted-foreground">
                Advanced machine learning models for credit risk assessment
              </p>
            </div>
            <div className="p-6 rounded-lg bg-card">
              <h3 className="font-semibold mb-2">👁️ Vision Analysis</h3>
              <p className="text-sm text-muted-foreground">
                Gemini Vision AI analyzes business photos for socioeconomic indicators
              </p>
            </div>
            <div className="p-6 rounded-lg bg-card">
              <h3 className="font-semibold mb-2">📝 NLP Insights</h3>
              <p className="text-sm text-muted-foreground">
                Extract valuable insights from field officer notes using NLP
              </p>
            </div>
            <div className="p-6 rounded-lg bg-card">
              <h3 className="font-semibold mb-2">💰 Income Validation</h3>
              <p className="text-sm text-muted-foreground">
                Reality check for claimed income against business indicators
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
