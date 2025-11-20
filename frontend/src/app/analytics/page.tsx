"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { loansAPI } from "@/lib/api";
import type { LoansStatistics } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SiteHeader } from "@/components/site-header";

export default function AnalyticsPage() {
  const [statistics, setStatistics] = useState<LoansStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchStatistics() {
      try {
        setLoading(true);
        const data = await loansAPI.statistics();
        setStatistics(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch statistics");
      } finally {
        setLoading(false);
      }
    }

    fetchStatistics();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <>
      <SiteHeader />
      <div className="flex flex-1 flex-col">
        <div className="container mx-auto px-4 py-8">

        <div className="mb-8">
          <h1 className="text-3xl font-bold">Portfolio Analytics</h1>
          <p className="text-muted-foreground mt-2">
            Comprehensive overview of loan portfolio performance and metrics
          </p>
        </div>

        {error && (
          <div className="bg-destructive/10 text-destructive px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Loading analytics...</p>
          </div>
        ) : statistics && (
          <div className="space-y-6">
            {/* Loan Portfolio Section */}
            <Card>
              <CardHeader>
                <CardTitle>Loan Portfolio Overview</CardTitle>
                <CardDescription>Summary of all loan activities</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-6">
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Total Loans</div>
                    <div className="text-3xl font-bold">{statistics.loan_portfolio.total_loans}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Active</div>
                    <div className="text-3xl font-bold text-blue-600">{statistics.loan_portfolio.active_loans}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Completed</div>
                    <div className="text-3xl font-bold text-green-600">{statistics.loan_portfolio.completed_loans}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Defaulted</div>
                    <div className="text-3xl font-bold text-red-600">{statistics.loan_portfolio.defaulted_loans}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Completion Rate</div>
                    <div className="text-3xl font-bold">{statistics.loan_portfolio.completion_rate}%</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Financial Summary Section */}
            <Card>
              <CardHeader>
                <CardTitle>Financial Summary</CardTitle>
                <CardDescription>Monetary flow and collection performance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Total Disbursed</div>
                    <div className="text-2xl font-bold">{formatCurrency(statistics.financial_summary.total_disbursed)}</div>
                    <div className="text-xs text-muted-foreground mt-1">Principal amount lent</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Expected Repayment</div>
                    <div className="text-2xl font-bold">{formatCurrency(statistics.financial_summary.total_expected_repayment)}</div>
                    <div className="text-xs text-muted-foreground mt-1">Total with interest</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Total Collected</div>
                    <div className="text-2xl font-bold text-green-600">{formatCurrency(statistics.financial_summary.total_collected)}</div>
                    <div className="text-xs text-muted-foreground mt-1">Payments received</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Outstanding</div>
                    <div className="text-2xl font-bold text-orange-600">{formatCurrency(statistics.financial_summary.outstanding_amount)}</div>
                    <div className="text-xs text-muted-foreground mt-1">Amount pending</div>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-muted-foreground">Collection Rate</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        Percentage of expected amount collected
                      </div>
                    </div>
                    <div className="text-4xl font-bold text-green-600">
                      {statistics.financial_summary.collection_rate}%
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Repayment Behavior Section */}
            <Card>
              <CardHeader>
                <CardTitle>Repayment Behavior</CardTitle>
                <CardDescription>Payment patterns and timeliness metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-4 gap-6">
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Total Payments</div>
                    <div className="text-3xl font-bold">{statistics.repayment_behavior.total_payments}</div>
                    <div className="text-xs text-muted-foreground mt-1">All payment transactions</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">On-Time</div>
                    <div className="text-3xl font-bold text-green-600">{statistics.repayment_behavior.on_time_payments}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {((statistics.repayment_behavior.on_time_payments / statistics.repayment_behavior.total_payments) * 100).toFixed(1)}% of total
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Late Payments</div>
                    <div className="text-3xl font-bold text-orange-600">{statistics.repayment_behavior.late_payments}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {((statistics.repayment_behavior.late_payments / statistics.repayment_behavior.total_payments) * 100).toFixed(1)}% of total
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Avg Days Overdue</div>
                    <div className="text-3xl font-bold">{statistics.repayment_behavior.average_days_overdue}</div>
                    <div className="text-xs text-muted-foreground mt-1">For late payments</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Key Insights */}
            <Card>
              <CardHeader>
                <CardTitle>Key Insights</CardTitle>
                <CardDescription>Portfolio health indicators</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div>
                      <div className="font-semibold">Strong Collection Performance</div>
                      <div className="text-sm text-muted-foreground">
                        Collection rate of {statistics.financial_summary.collection_rate}% indicates healthy repayment behavior
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div>
                      <div className="font-semibold">Active Portfolio</div>
                      <div className="text-sm text-muted-foreground">
                        {statistics.loan_portfolio.active_loans} active loans representing {
                          ((statistics.loan_portfolio.active_loans / statistics.loan_portfolio.total_loans) * 100).toFixed(1)
                        }% of total portfolio
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div>
                      <div className="font-semibold">Timely Payments</div>
                      <div className="text-sm text-muted-foreground">
                        {statistics.repayment_behavior.on_time_payments} on-time payments with average {statistics.repayment_behavior.average_days_overdue} days overdue when late
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
    </>
  );
}
