"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { borrowersAPI, creditScoringAPI } from "@/lib/api";
import type { Borrower, CreditAssessment } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SiteHeader } from "@/components/site-header";

export default function CreditAssessmentPage() {
  const [borrowers, setBorrowers] = useState<Borrower[]>([]);
  const [selectedBorrowerId, setSelectedBorrowerId] = useState<string>("");
  const [assessment, setAssessment] = useState<CreditAssessment | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchBorrowers() {
      try {
        const data = await borrowersAPI.list({ limit: 100 });
        setBorrowers(data);
        if (data.length > 0) {
          setSelectedBorrowerId(data[0].id);
        }
      } catch (err) {
        console.error("Failed to fetch borrowers:", err);
      }
    }
    fetchBorrowers();
  }, []);

  async function handleAssess() {
    if (!selectedBorrowerId) return;

    setLoading(true);
    setError(null);
    setAssessment(null);

    try {
      const result = await creditScoringAPI.assess(selectedBorrowerId, {
        include_photos: false,
        include_field_notes: false,
        save_to_database: true,
      });
      setAssessment(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Assessment failed");
    } finally {
      setLoading(false);
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'very_high': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const selectedBorrower = borrowers.find(b => b.id === selectedBorrowerId);

  return (
    <>
      <SiteHeader />
      <div className="flex flex-1 flex-col">
        <div className="container mx-auto px-4 py-8">

        <div className="mb-8">
          <h1 className="text-3xl font-bold">Credit Assessment</h1>
          <p className="text-muted-foreground mt-2">
            AI-powered multimodal credit scoring with income validation
          </p>
        </div>

        {/* Borrower Selection */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Select Borrower</CardTitle>
            <CardDescription>Choose a borrower to assess their creditworthiness</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Select value={selectedBorrowerId} onValueChange={setSelectedBorrowerId}>
                <SelectTrigger className="w-full max-w-md">
                  <SelectValue placeholder="Select borrower" />
                </SelectTrigger>
                <SelectContent>
                  {borrowers.map((borrower) => (
                    <SelectItem key={borrower.id} value={borrower.id}>
                      {borrower.full_name} - {borrower.business_type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button onClick={handleAssess} disabled={loading || !selectedBorrowerId}>
                {loading ? "Assessing..." : "Run Assessment"}
              </Button>
            </div>

            {selectedBorrower && (
              <div className="mt-4 p-4 bg-muted rounded-lg">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Age:</span> {selectedBorrower.age}
                  </div>
                  <div>
                    <span className="text-muted-foreground">Business:</span> {selectedBorrower.business_type}
                  </div>
                  <div>
                    <span className="text-muted-foreground">Income:</span> {formatCurrency(selectedBorrower.claimed_monthly_income)}
                  </div>
                  <div>
                    <span className="text-muted-foreground">Years:</span> {selectedBorrower.years_in_business || 0}
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {error && (
          <div className="bg-destructive/10 text-destructive px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {assessment && (
          <div className="space-y-6">
            {/* Credit Score Card */}
            <Card>
              <CardHeader>
                <CardTitle>Credit Score</CardTitle>
                <CardDescription>Multimodal AI assessment results</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <div className="text-5xl font-bold">{assessment.final_credit_score}</div>
                    <div className="text-sm text-muted-foreground mt-1">out of 100</div>
                  </div>
                  <div className={`px-4 py-2 rounded-lg border-2 font-semibold ${getRiskColor(assessment.risk_category)}`}>
                    {assessment.risk_category.toUpperCase()} RISK
                  </div>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <div className="p-4 bg-muted rounded-lg">
                    <div className="text-sm text-muted-foreground mb-1">ML Baseline</div>
                    <div className="text-2xl font-bold">{assessment.ml_baseline_score}</div>
                  </div>
                  <div className="p-4 bg-muted rounded-lg">
                    <div className="text-sm text-muted-foreground mb-1">Vision Adjustment</div>
                    <div className="text-2xl font-bold">{assessment.vision_score_adjustment > 0 ? '+' : ''}{assessment.vision_score_adjustment}</div>
                  </div>
                  <div className="p-4 bg-muted rounded-lg">
                    <div className="text-sm text-muted-foreground mb-1">NLP Adjustment</div>
                    <div className="text-2xl font-bold">{assessment.nlp_score_adjustment > 0 ? '+' : ''}{assessment.nlp_score_adjustment}</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Income Validation Card */}
            {assessment.income_validation && (
              <Card>
                <CardHeader>
                  <CardTitle>Income Reality Check</CardTitle>
                  <CardDescription>AI-powered income validation</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6 mb-4">
                    <div>
                      <div className="text-sm text-muted-foreground mb-1">Claimed Income</div>
                      <div className="text-2xl font-bold">{formatCurrency(assessment.income_validation.claimed_income)}</div>
                      <div className="text-xs text-muted-foreground mt-1">Borrower's stated income</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground mb-1">AI Estimated Income</div>
                      <div className="text-2xl font-bold text-blue-600">{formatCurrency(assessment.income_validation.ai_estimated_income)}</div>
                      <div className="text-xs text-muted-foreground mt-1">Based on multimodal analysis</div>
                    </div>
                  </div>

                  <div className="p-4 bg-muted rounded-lg mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Income Consistency Score</span>
                      <span className="text-lg font-bold">{assessment.income_validation.income_consistency_score.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full transition-all"
                        style={{ width: `${assessment.income_validation.income_consistency_score}%` }}
                      />
                    </div>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <div className="text-sm font-medium mb-2">Assessment</div>
                    <p className="text-sm text-muted-foreground">{assessment.income_validation.assessment}</p>
                    <div className="mt-2 text-xs text-muted-foreground">
                      Variance: {assessment.income_validation.variance_percentage > 0 ? '+' : ''}{assessment.income_validation.variance_percentage.toFixed(1)}%
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Loan Recommendation Card */}
            {assessment.loan_recommendation && (
              <Card>
                <CardHeader>
                  <CardTitle>Loan Recommendation</CardTitle>
                  <CardDescription>Optimal loan sizing based on risk profile</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6 mb-4">
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                      <div className="text-sm text-green-700 mb-1">Recommended Loan</div>
                      <div className="text-3xl font-bold text-green-700">{formatCurrency(assessment.loan_recommendation.recommended_loan_amount)}</div>
                      <div className="text-xs text-green-600 mt-1">Conservative 80% of max</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground mb-1">Weekly Repayment</div>
                      <div className="text-2xl font-bold">{formatCurrency(assessment.loan_recommendation.weekly_repayment)}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        Over {assessment.loan_recommendation.recommended_term_weeks} weeks
                      </div>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-3 gap-4 mb-4">
                    <div className="p-3 bg-muted rounded-lg">
                      <div className="text-xs text-muted-foreground mb-1">Max Safe Loan</div>
                      <div className="text-lg font-semibold">{formatCurrency(assessment.loan_recommendation.max_safe_loan_amount)}</div>
                    </div>
                    <div className="p-3 bg-muted rounded-lg">
                      <div className="text-xs text-muted-foreground mb-1">Repayment Ratio</div>
                      <div className="text-lg font-semibold">{assessment.loan_recommendation.repayment_to_income_ratio.toFixed(1)}%</div>
                    </div>
                    <div className="p-3 bg-muted rounded-lg">
                      <div className="text-xs text-muted-foreground mb-1">Confidence</div>
                      <div className="text-lg font-semibold">{(assessment.loan_recommendation.recommendation_confidence * 100).toFixed(0)}%</div>
                    </div>
                  </div>

                  <div className="p-4 border rounded-lg bg-blue-50 border-blue-200">
                    <div className="text-sm font-medium text-blue-900 mb-2">Justification</div>
                    <p className="text-sm text-blue-800">{assessment.loan_recommendation.justification}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Risk Explanation Card */}
            {assessment.risk_explanation && (
              <Card>
                <CardHeader>
                  <CardTitle>Risk Explanation (Gemini AI)</CardTitle>
                  <CardDescription>Human-readable assessment in Bahasa Indonesia</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                    {assessment.risk_explanation}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
    </>
  );
}
