import type {
  Borrower,
  Loan,
  CreditAssessment,
  Photo,
  FieldNote,
  LoansStatistics,
  BorrowerSummary,
} from "./types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const API_V1 = `${API_BASE_URL}/api/v1`

// Helper function for API calls
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_V1}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "An error occurred" }))
    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
  }

  return response.json()
}

// Borrowers API
export const borrowersAPI = {
  async list(params?: { limit?: number; offset?: number; business_type?: string; province?: string }): Promise<Borrower[]> {
    const query = new URLSearchParams()
    if (params?.limit) query.append("limit", params.limit.toString())
    if (params?.offset) query.append("offset", params.offset.toString())
    if (params?.business_type) query.append("business_type", params.business_type)
    if (params?.province) query.append("province", params.province)

    return fetchAPI<Borrower[]>(`/borrowers?${query}`)
  },

  async get(id: string): Promise<Borrower> {
    return fetchAPI<Borrower>(`/borrowers/${id}`)
  },

  async create(data: Partial<Borrower>): Promise<Borrower> {
    return fetchAPI<Borrower>("/borrowers", {
      method: "POST",
      body: JSON.stringify(data),
    })
  },

  async getLoans(id: string): Promise<{ borrower_id: string; total_loans: number; loans: Loan[] }> {
    return fetchAPI(`/borrowers/${id}/loans`)
  },

  async getPhotos(id: string): Promise<{ borrower_id: string; total_photos: number; photos: Photo[] }> {
    return fetchAPI(`/borrowers/${id}/photos`)
  },

  async getFieldNotes(id: string): Promise<{ borrower_id: string; total_notes: number; field_notes: FieldNote[] }> {
    return fetchAPI(`/borrowers/${id}/field-notes`)
  },

  async getSummary(id: string): Promise<BorrowerSummary> {
    return fetchAPI<BorrowerSummary>(`/borrowers/${id}/summary`)
  },
}

// Loans API
export const loansAPI = {
  async list(params?: { limit?: number; offset?: number; status?: string }): Promise<Loan[]> {
    const query = new URLSearchParams()
    if (params?.limit) query.append("limit", params.limit.toString())
    if (params?.offset) query.append("offset", params.offset.toString())
    if (params?.status) query.append("status", params.status)

    return fetchAPI<Loan[]>(`/loans?${query}`)
  },

  async get(id: string): Promise<Loan> {
    return fetchAPI<Loan>(`/loans/${id}`)
  },

  async create(data: Partial<Loan>): Promise<Loan> {
    return fetchAPI<Loan>("/loans", {
      method: "POST",
      body: JSON.stringify(data),
    })
  },

  async statistics(): Promise<LoansStatistics> {
    return fetchAPI<LoansStatistics>("/loans/statistics")
  },
}

// Credit Scoring API
export const creditScoringAPI = {
  async assess(params: {
    borrower_id: string
    include_photos?: boolean
    include_field_notes?: boolean
    save_to_database?: boolean
  }): Promise<CreditAssessment> {
    return fetchAPI<CreditAssessment>("/credit-scoring/assess", {
      method: "POST",
      body: JSON.stringify(params),
    })
  },

  async getHistory(borrowerId: string, limit?: number): Promise<{ borrower_id: string; total_assessments: number; assessments: CreditAssessment[] }> {
    const query = limit ? `?limit=${limit}` : ""
    return fetchAPI(`/credit-scoring/${borrowerId}/history${query}`)
  },

  async getLatest(borrowerId: string): Promise<CreditAssessment> {
    return fetchAPI<CreditAssessment>(`/credit-scoring/${borrowerId}/latest`)
  },

  async getRiskDistribution(): Promise<any> {
    return fetchAPI("/credit-scoring/statistics/risk-distribution")
  },

  async batchAssess(borrowerIds: string[], saveToDatabase?: boolean): Promise<any> {
    return fetchAPI("/credit-scoring/batch-assess", {
      method: "POST",
      body: JSON.stringify({
        borrower_ids: borrowerIds,
        save_to_database: saveToDatabase ?? true,
      }),
    })
  },
}

// Photos API
export const photosAPI = {
  async list(borrowerId?: string): Promise<Photo[]> {
    const query = borrowerId ? `?borrower_id=${borrowerId}` : ""
    return fetchAPI<Photo[]>(`/photos${query}`)
  },

  async get(id: string): Promise<Photo> {
    return fetchAPI<Photo>(`/photos/${id}`)
  },

  async upload(borrowerId: string, file: File, photoType: string, caption?: string): Promise<Photo> {
    const formData = new FormData()
    formData.append("file", file)
    formData.append("borrower_id", borrowerId)
    formData.append("photo_type", photoType)
    if (caption) formData.append("caption", caption)

    const response = await fetch(`${API_V1}/photos/upload`, {
      method: "POST",
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Upload failed" }))
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`)
    }

    return response.json()
  },

  async analyze(photoId: string): Promise<{ photo_id: string; analysis: any }> {
    return fetchAPI(`/photos/${photoId}/analyze`, {
      method: "POST",
    })
  },
}

// Field Notes API
export const fieldNotesAPI = {
  async list(borrowerId?: string): Promise<FieldNote[]> {
    const query = borrowerId ? `?borrower_id=${borrowerId}` : ""
    return fetchAPI<FieldNote[]>(`/field-notes${query}`)
  },

  async get(id: string): Promise<FieldNote> {
    return fetchAPI<FieldNote>(`/field-notes/${id}`)
  },

  async create(data: Partial<FieldNote>): Promise<FieldNote> {
    return fetchAPI<FieldNote>("/field-notes", {
      method: "POST",
      body: JSON.stringify(data),
    })
  },

  async extract(noteId: string): Promise<{ note_id: string; extraction: any }> {
    return fetchAPI(`/field-notes/${noteId}/extract`, {
      method: "POST",
    })
  },
}
