"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { loansAPI } from "@/lib/api";
import type { Loan, LoansStatistics } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react";

export default function LoansPage() {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [statistics, setStatistics] = useState<LoansStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [loansData, statsData] = await Promise.all([
          loansAPI.list({ limit: 50 }),
          loansAPI.statistics(),
        ]);
        setLoans(loansData);
        setStatistics(statsData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch loans data");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  // Filter loans based on search term
  const filteredLoans = loans.filter(loan =>
    formatCurrency(loan.loan_amount).toLowerCase().includes(searchTerm.toLowerCase()) ||
    loan.loan_status.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (loan.purpose && loan.purpose.toLowerCase().includes(searchTerm.toLowerCase())) ||
    loan.interest_rate.toString().includes(searchTerm) ||
    loan.loan_term_weeks.toString().includes(searchTerm)
  );

  // Pagination logic
  const totalPages = Math.ceil(filteredLoans.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentLoans = filteredLoans.slice(startIndex, endIndex);

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  return (
    <div className="flex flex-1 flex-col">
      <div className="container mx-auto px-4 py-8">

        {error && (
          <div className="bg-destructive/10 text-destructive px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Loading loans data...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Statistics Dashboard */}
            {statistics && (
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardDescription>Total Loans</CardDescription>
                    <CardTitle className="text-3xl">{statistics.loan_portfolio.total_loans}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs space-y-1">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Active:</span>
                        <Badge variant="default">{statistics.loan_portfolio.active_loans}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Completed:</span>
                        <Badge variant="secondary">{statistics.loan_portfolio.completed_loans}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Defaulted:</span>
                        <Badge variant="destructive">{statistics.loan_portfolio.defaulted_loans}</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardDescription>Total Disbursed</CardDescription>
                    <CardTitle className="text-2xl">{formatCurrency(statistics.financial_summary.total_disbursed)}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs text-muted-foreground">
                      Total amount disbursed across all loans
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardDescription>Collection Rate</CardDescription>
                    <CardTitle className="text-3xl">{statistics.financial_summary.collection_rate}%</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs space-y-1">
                      <div className="text-muted-foreground">
                        Collected: {formatCurrency(statistics.financial_summary.total_collected)}
                      </div>
                      <div className="text-muted-foreground">
                        Outstanding: {formatCurrency(statistics.financial_summary.outstanding_amount)}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardDescription>Repayment Behavior</CardDescription>
                    <CardTitle className="text-3xl">{statistics.repayment_behavior.on_time_payments}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-xs space-y-1">
                      <div className="text-muted-foreground">
                        On-time payments out of {statistics.repayment_behavior.total_payments}
                      </div>
                      <div className="text-muted-foreground">
                        Avg days overdue: {statistics.repayment_behavior.average_days_overdue}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Loans Table */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Loans</CardTitle>
                <CardDescription>
                  Showing {startIndex + 1}-{Math.min(endIndex, filteredLoans.length)} of {filteredLoans.length} loans
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                  <Input
                    placeholder="Search by amount, status, purpose, rate, or term..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="max-w-md focus:ring-2 focus:ring-primary/20"
                  />
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground whitespace-nowrap">Rows per page:</span>
                    <Select value={itemsPerPage.toString()} onValueChange={(value) => setItemsPerPage(Number(value))}>
                      <SelectTrigger className="w-[70px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="5">5</SelectItem>
                        <SelectItem value="10">10</SelectItem>
                        <SelectItem value="20">20</SelectItem>
                        <SelectItem value="50">50</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Amount</TableHead>
                        <TableHead>Interest Rate</TableHead>
                        <TableHead>Term</TableHead>
                        <TableHead>Disbursement</TableHead>
                        <TableHead>Expected Repayment</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Purpose</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {currentLoans.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                            No loans found
                          </TableCell>
                        </TableRow>
                      ) : (
                        currentLoans.map((loan) => (
                          <TableRow key={loan.id}>
                            <TableCell className="font-medium">{formatCurrency(loan.loan_amount)}</TableCell>
                            <TableCell>{loan.interest_rate}%</TableCell>
                            <TableCell>{loan.loan_term_weeks} weeks</TableCell>
                            <TableCell>{formatDate(loan.disbursement_date)}</TableCell>
                            <TableCell>{formatDate(loan.expected_repayment_date)}</TableCell>
                            <TableCell>
                              <Badge variant={
                                loan.loan_status === "active" ? "default" :
                                loan.loan_status === "completed" ? "secondary" :
                                "destructive"
                              }>
                                {loan.loan_status}
                              </Badge>
                            </TableCell>
                            <TableCell className="max-w-xs truncate">{loan.purpose || "-"}</TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </div>

                {/* Pagination Controls */}
                {filteredLoans.length > 0 && (
                  <div className="flex items-center justify-between mt-4">
                    <div className="text-sm text-muted-foreground">
                      Page {currentPage} of {totalPages}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                        disabled={currentPage === 1}
                      >
                        <ChevronLeftIcon className="h-4 w-4" />
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                        disabled={currentPage === totalPages}
                      >
                        Next
                        <ChevronRightIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
