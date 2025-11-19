"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { borrowersAPI } from "@/lib/api";
import type { Borrower } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

export default function BorrowersPage() {
  const [borrowers, setBorrowers] = useState<Borrower[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchBorrowers() {
      try {
        setLoading(true);
        const data = await borrowersAPI.list({ limit: 50 });
        setBorrowers(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch borrowers");
      } finally {
        setLoading(false);
      }
    }

    fetchBorrowers();
  }, []);

  const filteredBorrowers = borrowers.filter(borrower =>
    borrower.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    borrower.business_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    borrower.province?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link href="/">
            <Button variant="ghost">← Back to Home</Button>
          </Link>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Borrowers</CardTitle>
            <CardDescription>
              View and manage all borrower profiles
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="mb-6">
              <Input
                placeholder="Search by name, business type, or province..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="max-w-md"
              />
            </div>

            {error && (
              <div className="bg-destructive/10 text-destructive px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            {loading ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">Loading borrowers...</p>
              </div>
            ) : (
              <>
                <div className="mb-4 text-sm text-muted-foreground">
                  Showing {filteredBorrowers.length} of {borrowers.length} borrowers
                </div>

                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Age</TableHead>
                        <TableHead>Business</TableHead>
                        <TableHead>Monthly Income</TableHead>
                        <TableHead>Province</TableHead>
                        <TableHead>Bank Account</TableHead>
                        <TableHead>Financial Literacy</TableHead>
                        <TableHead>Action</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredBorrowers.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                            No borrowers found
                          </TableCell>
                        </TableRow>
                      ) : (
                        filteredBorrowers.map((borrower) => (
                          <TableRow key={borrower.id}>
                            <TableCell className="font-medium">{borrower.full_name}</TableCell>
                            <TableCell>{borrower.age}</TableCell>
                            <TableCell className="max-w-xs truncate">{borrower.business_type}</TableCell>
                            <TableCell>{formatCurrency(borrower.claimed_monthly_income)}</TableCell>
                            <TableCell>{borrower.province || "-"}</TableCell>
                            <TableCell>
                              <Badge variant={borrower.has_bank_account ? "default" : "secondary"}>
                                {borrower.has_bank_account ? "Yes" : "No"}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              {borrower.financial_literacy_score ? (
                                <Badge variant={borrower.financial_literacy_score >= 70 ? "default" : "secondary"}>
                                  {borrower.financial_literacy_score}
                                </Badge>
                              ) : (
                                "-"
                              )}
                            </TableCell>
                            <TableCell>
                              <Link href={`/borrowers/${borrower.id}`}>
                                <Button size="sm" variant="outline">View</Button>
                              </Link>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
