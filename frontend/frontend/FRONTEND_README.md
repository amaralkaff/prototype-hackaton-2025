# Amarta AI - Frontend

Next.js frontend application for the Amarta AI credit scoring system with shadcn/ui components.

## Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible UI components
- **Lucide React** - Icon library

## Features

### Pages

1. **Home (`/`)** - Landing page with navigation to all sections
2. **Borrowers (`/borrowers`)** - List view with search and filtering
3. **Borrower Detail (`/borrowers/[id]`)** - Comprehensive borrower profile
4. **Loans (`/loans`)** - Loan portfolio with statistics dashboard
5. **Analytics (`/analytics`)** - Portfolio performance metrics

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running on http://localhost:8000

### Installation

```bash
npm install
```

### Development

```bash
# Run development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   ├── components/ui/          # shadcn/ui components
│   └── lib/
│       ├── api.ts             # API client
│       ├── types.ts           # TypeScript interfaces
│       └── utils.ts           # Utilities
├── components.json            # shadcn/ui config
└── .env.local                 # Environment variables
```

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API base URL (default: http://localhost:8000)
