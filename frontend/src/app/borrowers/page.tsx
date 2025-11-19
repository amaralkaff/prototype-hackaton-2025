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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react";

export default function BorrowersPage() {
  const [borrowers, setBorrowers] = useState<Borrower[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  useEffect(() => {
    async function fetchBorrowers() {
      try {
        setLoading(true);
        const data = await borrowersAPI.list({ limit: 100 });
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

  // Pagination logic
  const totalPages = Math.ceil(filteredBorrowers.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentBorrowers = filteredBorrowers.slice(startIndex, endIndex);

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="flex flex-1 flex-col">
      <div className="container mx-auto px-4 py-8">

        <Card className="shadow-lg">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-2xl">Borrowers</CardTitle>
                <CardDescription className="text-base mt-2">
                  View and manage all borrower profiles
                </CardDescription>
              </div>
              <Link href="/borrowers/new">
                <Button className="bg-primary hover:bg-primary/90">+ Create Borrower</Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
              <Input
                placeholder="Search by name, business type, or province..."
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

            {error && (
              <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg mb-4 border border-destructive/20">
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
                  Showing {startIndex + 1}-{Math.min(endIndex, filteredBorrowers.length)} of {filteredBorrowers.length} borrowers
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
                      {currentBorrowers.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                            No borrowers found
                          </TableCell>
                        </TableRow>
                      ) : (
                        currentBorrowers.map((borrower) => (
                          <TableRow key={borrower.id}>
                            <TableCell className="font-medium">{borrower.full_name}</TableCell>
                            <TableCell>{borrower.age}</TableCell>
                            <TableCell className="max-w-xs truncate">{borrower.business_type}</TableCell>
                            <TableCell>{formatCurrency(borrower.claimed_monthly_income)}</TableCell>
                            <TableCell>{borrower.province || "-"}</TableCell>
                            <TableCell>
                              <Badge
                                variant={borrower.has_bank_account ? "default" : "secondary"}
                                className={borrower.has_bank_account ? "bg-primary hover:bg-primary/90" : ""}
                              >
                                {borrower.has_bank_account ? "Yes" : "No"}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              {borrower.financial_literacy_score ? (
                                <Badge
                                  variant={borrower.financial_literacy_score >= 70 ? "default" : "secondary"}
                                  className={borrower.financial_literacy_score >= 70 ? "bg-primary hover:bg-primary/90" : ""}
                                >
                                  {borrower.financial_literacy_score}
                                </Badge>
                              ) : (
                                "-"
                              )}
                            </TableCell>
                            <TableCell>
                              <Link href={`/borrowers/${borrower.id}`}>
                                <Button size="sm" variant="outline" className="hover:bg-primary/10 hover:text-primary hover:border-primary">View</Button>
                              </Link>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </div>

                {/* Pagination Controls */}
                {filteredBorrowers.length > 0 && (
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
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
