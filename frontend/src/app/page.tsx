"use client"

import { useEffect, useState } from "react"
import { ChartAreaInteractive } from "@/components/chart-area-interactive"
import { SectionCards } from "@/components/section-cards"
import { SiteHeader } from "@/components/site-header"
import { loansAPI } from "@/lib/api"
import type { Loan } from "@/lib/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react"

export default function Home() {
  const [loans, setLoans] = useState<Loan[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(10)

  useEffect(() => {
    async function fetchLoans() {
      try {
        setLoading(true)
        const data = await loansAPI.list({ limit: 10 })
        setLoans(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch loans")
      } finally {
        setLoading(false)
      }
    }

    fetchLoans()
  }, [])

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  // Filter loans based on search term
  const filteredLoans = loans.filter(loan =>
    formatCurrency(loan.loan_amount).toLowerCase().includes(searchTerm.toLowerCase()) ||
    loan.loan_status.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (loan.purpose && loan.purpose.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  // Pagination logic
  const totalPages = Math.ceil(filteredLoans.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentLoans = filteredLoans.slice(startIndex, endIndex)

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm])

  return (
    <>
      <SiteHeader />
      <div className="flex flex-1 flex-col">
        <div className="@container/main flex flex-1 flex-col gap-2">
          <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
            <SectionCards />
            <div className="px-4 lg:px-6">
              <ChartAreaInteractive />
            </div>

            {/* Recent Loans Table */}
            <div className="px-4 lg:px-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Loans</CardTitle>
                  <CardDescription>Showing {startIndex + 1}-{Math.min(endIndex, filteredLoans.length)} of {filteredLoans.length} recent loans</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                    <Input
                      placeholder="Search by amount, status, or purpose..."
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
                    <div className="text-center py-8">
                      <p className="text-muted-foreground">Loading recent loans...</p>
                    </div>
                  ) : (
                    <>
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
                                  No recent loans found
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
                    </>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
