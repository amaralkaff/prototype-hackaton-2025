"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { loansAPI, creditScoringAPI } from "@/lib/api";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";

export default function DashboardPage() {
  const [loansStats, setLoansStats] = useState<any>(null);
  const [riskDistribution, setRiskDistribution] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        setLoading(true);
        const [loans, risk] = await Promise.all([
          loansAPI.statistics(),
          creditScoringAPI.riskDistribution(),
        ]);
        setLoansStats(loans);
        setRiskDistribution(risk);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch dashboard data");
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      notation: 'compact',
      compactDisplay: 'short',
    }).format(amount);
  };

  const RISK_COLORS = {
    low: '#10b981',
    medium: '#f59e0b',
    high: '#ef4444',
  };

  const STATUS_COLORS = {
    active: '#3b82f6',
    completed: '#10b981',
    defaulted: '#ef4444',
    pending: '#f59e0b',
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Loading dashboard...</p>
      </div>
    );
  }

  if (error || !loansStats || !riskDistribution) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <Link href="/">
            <Button variant="ghost">← Back to Home</Button>
          </Link>
          <div className="bg-destructive/10 text-destructive px-4 py-3 rounded mt-4">
            {error || "Failed to load dashboard data"}
          </div>
        </div>
      </div>
    );
  }

  // Prepare risk distribution data for pie chart
  const riskChartData = Object.entries(riskDistribution.risk_distribution || {}).map(([key, value]: [string, any]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1) + ' Risk',
    value: value.count,
    percentage: value.percentage,
  }));

  // Prepare loan status data for bar chart
  const statusChartData = Object.entries(loansStats.status_breakdown || {}).map(([key, value]: [string, any]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    count: value.count,
    amount: value.total_amount,
  }));

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link href="/">
            <Button variant="ghost">← Back to Home</Button>
          </Link>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Overview of loan portfolio and credit assessments</p>
        </div>

        {/* Key Metrics */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Loans</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{loansStats.total_loans}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Active: {loansStats.active_loans}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Disbursed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(loansStats.total_amount_disbursed)}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Outstanding: {formatCurrency(loansStats.total_outstanding)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Avg Credit Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{riskDistribution.average_score?.toFixed(1) || 'N/A'}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {riskDistribution.total_assessments} assessments
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Default Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {loansStats.status_breakdown?.defaulted
                  ? ((loansStats.status_breakdown.defaulted.count / loansStats.total_loans) * 100).toFixed(1)
                  : '0'}%
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {loansStats.status_breakdown?.defaulted?.count || 0} defaulted
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Risk Distribution Pie Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Distribution</CardTitle>
              <CardDescription>Credit assessment risk categories</CardDescription>
            </CardHeader>
            <CardContent>
              {riskChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={riskChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.percentage.toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {riskChartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={RISK_COLORS[entry.name.toLowerCase().split(' ')[0] as keyof typeof RISK_COLORS] || '#94a3b8'}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-center text-muted-foreground py-8">No risk data available</p>
              )}
            </CardContent>
          </Card>

          {/* Loan Status Bar Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Loan Status Breakdown</CardTitle>
              <CardDescription>Loans by status category</CardDescription>
            </CardHeader>
            <CardContent>
              {statusChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={statusChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          return (
                            <div className="bg-background border rounded p-2 shadow-lg">
                              <p className="font-semibold">{payload[0].payload.name}</p>
                              <p className="text-sm">Count: {payload[0].value}</p>
                              <p className="text-sm">Amount: {formatCurrency(payload[0].payload.amount)}</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar
                      dataKey="count"
                      fill="#3b82f6"
                      radius={[8, 8, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-center text-muted-foreground py-8">No loan data available</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Loan Statistics Details */}
        <div className="grid md:grid-cols-2 gap-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Loan Statistics</CardTitle>
              <CardDescription>Detailed portfolio metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-sm text-muted-foreground">Average Loan Amount:</dt>
                  <dd className="text-sm font-medium">{formatCurrency(loansStats.average_loan_amount)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-muted-foreground">Total Outstanding:</dt>
                  <dd className="text-sm font-medium">{formatCurrency(loansStats.total_outstanding)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-muted-foreground">Total Disbursed:</dt>
                  <dd className="text-sm font-medium">{formatCurrency(loansStats.total_amount_disbursed)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-muted-foreground">Active Loans:</dt>
                  <dd className="text-sm font-medium">{loansStats.active_loans} of {loansStats.total_loans}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Credit Assessment Summary</CardTitle>
              <CardDescription>Risk evaluation overview</CardDescription>
            </CardHeader>
            <CardContent>
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-sm text-muted-foreground">Total Assessments:</dt>
                  <dd className="text-sm font-medium">{riskDistribution.total_assessments}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-muted-foreground">Average Score:</dt>
                  <dd className="text-sm font-medium">{riskDistribution.average_score?.toFixed(1) || 'N/A'}/100</dd>
                </div>
                {Object.entries(riskDistribution.risk_distribution || {}).map(([key, value]: [string, any]) => (
                  <div key={key} className="flex justify-between">
                    <dt className="text-sm text-muted-foreground capitalize">{key} Risk:</dt>
                    <dd className="text-sm font-medium">{value.count} ({value.percentage.toFixed(1)}%)</dd>
                  </div>
                ))}
              </dl>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
