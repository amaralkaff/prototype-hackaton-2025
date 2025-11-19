"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { borrowersAPI } from "@/lib/api";
import type { BorrowerSummary } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function BorrowerDetailPage() {
  const params = useParams();
  const borrowerId = params.id as string;
  const [summary, setSummary] = useState<BorrowerSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchBorrowerSummary() {
      try {
        setLoading(true);
        const data = await borrowersAPI.summary(borrowerId);
        setSummary(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch borrower details");
      } finally {
        setLoading(false);
      }
    }

    if (borrowerId) {
      fetchBorrowerSummary();
    }
  }, [borrowerId]);

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

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Loading borrower details...</p>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <Link href="/borrowers">
            <Button variant="ghost">← Back to Borrowers</Button>
          </Link>
          <div className="bg-destructive/10 text-destructive px-4 py-3 rounded mt-4">
            {error || "Borrower not found"}
          </div>
        </div>
      </div>
    );
  }

  const { borrower, loans, photos, field_notes, credit_assessments } = summary;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link href="/borrowers">
            <Button variant="ghost">← Back to Borrowers</Button>
          </Link>
        </div>

        <div className="grid gap-6">
          {/* Borrower Profile */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-2xl">{borrower.full_name}</CardTitle>
                  <CardDescription>Borrower Profile</CardDescription>
                </div>
                <Badge variant="outline">{borrower.age} years old</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold mb-2">Personal Information</h3>
                  <dl className="space-y-2 text-sm">
                    <div><dt className="text-muted-foreground inline">Gender:</dt> <dd className="inline">{borrower.gender || "-"}</dd></div>
                    <div><dt className="text-muted-foreground inline">Marital Status:</dt> <dd className="inline">{borrower.marital_status || "-"}</dd></div>
                    <div><dt className="text-muted-foreground inline">Dependents:</dt> <dd className="inline">{borrower.num_dependents || 0}</dd></div>
                    <div><dt className="text-muted-foreground inline">Education:</dt> <dd className="inline">{borrower.education_level || "-"}</dd></div>
                    <div><dt className="text-muted-foreground inline">Phone:</dt> <dd className="inline">{borrower.phone_number || "-"}</dd></div>
                  </dl>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Location</h3>
                  <dl className="space-y-2 text-sm">
                    <div><dt className="text-muted-foreground inline">Village:</dt> <dd className="inline">{borrower.village || "-"}</dd></div>
                    <div><dt className="text-muted-foreground inline">District:</dt> <dd className="inline">{borrower.district || "-"}</dd></div>
                    <div><dt className="text-muted-foreground inline">Province:</dt> <dd className="inline">{borrower.province || "-"}</dd></div>
                  </dl>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Business Information</h3>
                  <dl className="space-y-2 text-sm">
                    <div><dt className="text-muted-foreground inline">Type:</dt> <dd className="inline">{borrower.business_type}</dd></div>
                    <div><dt className="text-muted-foreground inline">Description:</dt> <dd className="inline">{borrower.business_description || "-"}</dd></div>
                    <div><dt className="text-muted-foreground inline">Years in Business:</dt> <dd className="inline">{borrower.years_in_business || "-"}</dd></div>
                    <div><dt className="text-muted-foreground inline">Monthly Income:</dt> <dd className="inline font-semibold">{formatCurrency(borrower.claimed_monthly_income)}</dd></div>
                  </dl>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Financial Profile</h3>
                  <dl className="space-y-2 text-sm">
                    <div>
                      <dt className="text-muted-foreground inline">Bank Account:</dt>{" "}
                      <Badge variant={borrower.has_bank_account ? "default" : "secondary"} className="ml-2">
                        {borrower.has_bank_account ? "Yes" : "No"}
                      </Badge>
                    </div>
                    <div>
                      <dt className="text-muted-foreground inline">Financial Records:</dt>{" "}
                      <Badge variant={borrower.keeps_financial_records ? "default" : "secondary"} className="ml-2">
                        {borrower.keeps_financial_records ? "Yes" : "No"}
                      </Badge>
                    </div>
                    <div>
                      <dt className="text-muted-foreground inline">Financial Literacy:</dt>{" "}
                      {borrower.financial_literacy_score ? (
                        <Badge variant={borrower.financial_literacy_score >= 70 ? "default" : "secondary"} className="ml-2">
                          {borrower.financial_literacy_score}/100
                        </Badge>
                      ) : (
                        <span className="ml-2">-</span>
                      )}
                    </div>
                  </dl>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Loans */}
          <Card>
            <CardHeader>
              <CardTitle>Loans ({loans.total})</CardTitle>
              <CardDescription>Loan history and active loans</CardDescription>
            </CardHeader>
            <CardContent>
              {loans.total === 0 ? (
                <p className="text-center text-muted-foreground py-8">No loans found</p>
              ) : (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Amount</TableHead>
                        <TableHead>Interest Rate</TableHead>
                        <TableHead>Term</TableHead>
                        <TableHead>Disbursement Date</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Purpose</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {loans.items.map((loan) => (
                        <TableRow key={loan.id}>
                          <TableCell className="font-medium">{formatCurrency(loan.loan_amount)}</TableCell>
                          <TableCell>{loan.interest_rate}%</TableCell>
                          <TableCell>{loan.loan_term_weeks} weeks</TableCell>
                          <TableCell>{formatDate(loan.disbursement_date)}</TableCell>
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
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Additional Information Grid */}
          <div className="grid md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Photos ({photos.total})</CardTitle>
              </CardHeader>
              <CardContent>
                {photos.total === 0 ? (
                  <p className="text-sm text-muted-foreground">No photos uploaded</p>
                ) : (
                  <p className="text-sm">{photos.total} photo(s) available for analysis</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Field Notes ({field_notes.total})</CardTitle>
              </CardHeader>
              <CardContent>
                {field_notes.total === 0 ? (
                  <p className="text-sm text-muted-foreground">No field notes recorded</p>
                ) : (
                  <p className="text-sm">{field_notes.total} field visit(s) documented</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Credit Assessments ({credit_assessments.total})</CardTitle>
              </CardHeader>
              <CardContent>
                {credit_assessments.total === 0 ? (
                  <p className="text-sm text-muted-foreground">No assessments performed</p>
                ) : (
                  <p className="text-sm">{credit_assessments.total} assessment(s) completed</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
