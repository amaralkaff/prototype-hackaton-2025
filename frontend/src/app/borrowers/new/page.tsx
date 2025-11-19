"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";

export default function NewBorrowerPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    full_name: "",
    age: "",
    gender: "",
    phone_number: "",
    village: "",
    district: "",
    province: "",
    marital_status: "",
    num_dependents: "0",
    education_level: "",
    business_type: "",
    business_description: "",
    years_in_business: "",
    claimed_monthly_income: "",
    has_bank_account: false,
    keeps_financial_records: false,
    financial_literacy_score: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;

    if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate required fields
      if (!formData.full_name || !formData.age || !formData.business_type || !formData.claimed_monthly_income) {
        throw new Error("Please fill in all required fields");
      }

      // Convert numeric fields
      const payload = {
        full_name: formData.full_name,
        age: parseInt(formData.age),
        gender: formData.gender || null,
        phone_number: formData.phone_number || null,
        village: formData.village || null,
        district: formData.district || null,
        province: formData.province || null,
        marital_status: formData.marital_status || null,
        num_dependents: parseInt(formData.num_dependents) || 0,
        education_level: formData.education_level || null,
        business_type: formData.business_type,
        business_description: formData.business_description || null,
        years_in_business: formData.years_in_business ? parseFloat(formData.years_in_business) : null,
        claimed_monthly_income: parseFloat(formData.claimed_monthly_income),
        has_bank_account: formData.has_bank_account,
        keeps_financial_records: formData.keeps_financial_records,
        financial_literacy_score: formData.financial_literacy_score ? parseInt(formData.financial_literacy_score) : null,
      };

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/borrowers/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create borrower");
      }

      const newBorrower = await response.json();
      router.push(`/borrowers/${newBorrower.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create borrower");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link href="/borrowers">
            <Button variant="ghost">← Back to Borrowers</Button>
          </Link>
        </div>

        <Card className="max-w-4xl mx-auto">
          <CardHeader>
            <CardTitle className="text-2xl">Create New Borrower</CardTitle>
            <CardDescription>Add a new borrower to the system</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Personal Information */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Personal Information</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Full Name <span className="text-destructive">*</span>
                    </label>
                    <Input
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleChange}
                      required
                      placeholder="Enter full name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Age <span className="text-destructive">*</span>
                    </label>
                    <Input
                      type="number"
                      name="age"
                      value={formData.age}
                      onChange={handleChange}
                      required
                      min="18"
                      max="100"
                      placeholder="Age"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Gender</label>
                    <select
                      name="gender"
                      value={formData.gender}
                      onChange={handleChange}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="">Select gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Phone Number</label>
                    <Input
                      type="tel"
                      name="phone_number"
                      value={formData.phone_number}
                      onChange={handleChange}
                      placeholder="+62xxx"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Marital Status</label>
                    <select
                      name="marital_status"
                      value={formData.marital_status}
                      onChange={handleChange}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="">Select status</option>
                      <option value="single">Single</option>
                      <option value="married">Married</option>
                      <option value="divorced">Divorced</option>
                      <option value="widowed">Widowed</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Number of Dependents</label>
                    <Input
                      type="number"
                      name="num_dependents"
                      value={formData.num_dependents}
                      onChange={handleChange}
                      min="0"
                      placeholder="0"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Education Level</label>
                    <select
                      name="education_level"
                      value={formData.education_level}
                      onChange={handleChange}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="">Select education</option>
                      <option value="no_formal">No Formal Education</option>
                      <option value="primary">Primary</option>
                      <option value="junior_high">Junior High</option>
                      <option value="senior_high">Senior High</option>
                      <option value="diploma">Diploma</option>
                      <option value="bachelor">Bachelor</option>
                      <option value="postgraduate">Postgraduate</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Location */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Location</h3>
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Village</label>
                    <Input
                      name="village"
                      value={formData.village}
                      onChange={handleChange}
                      placeholder="Village name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">District</label>
                    <Input
                      name="district"
                      value={formData.district}
                      onChange={handleChange}
                      placeholder="District name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Province</label>
                    <Input
                      name="province"
                      value={formData.province}
                      onChange={handleChange}
                      placeholder="Province name"
                    />
                  </div>
                </div>
              </div>

              {/* Business Information */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Business Information</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Business Type <span className="text-destructive">*</span>
                    </label>
                    <select
                      name="business_type"
                      value={formData.business_type}
                      onChange={handleChange}
                      required
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="">Select business type</option>
                      <option value="agriculture">Agriculture</option>
                      <option value="retail">Retail</option>
                      <option value="food_service">Food Service</option>
                      <option value="crafts">Crafts</option>
                      <option value="transportation">Transportation</option>
                      <option value="services">Services</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Years in Business</label>
                    <Input
                      type="number"
                      name="years_in_business"
                      value={formData.years_in_business}
                      onChange={handleChange}
                      step="0.5"
                      min="0"
                      placeholder="0"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium mb-2">Business Description</label>
                    <textarea
                      name="business_description"
                      value={formData.business_description}
                      onChange={handleChange}
                      rows={3}
                      placeholder="Describe the business..."
                      className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Claimed Monthly Income (IDR) <span className="text-destructive">*</span>
                    </label>
                    <Input
                      type="number"
                      name="claimed_monthly_income"
                      value={formData.claimed_monthly_income}
                      onChange={handleChange}
                      required
                      min="0"
                      placeholder="5000000"
                    />
                  </div>
                </div>
              </div>

              {/* Financial Profile */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Financial Profile</h3>
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      name="has_bank_account"
                      checked={formData.has_bank_account}
                      onChange={handleChange}
                      className="h-4 w-4 rounded border-gray-300"
                      id="has_bank_account"
                    />
                    <label htmlFor="has_bank_account" className="text-sm font-medium">
                      Has Bank Account
                    </label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      name="keeps_financial_records"
                      checked={formData.keeps_financial_records}
                      onChange={handleChange}
                      className="h-4 w-4 rounded border-gray-300"
                      id="keeps_financial_records"
                    />
                    <label htmlFor="keeps_financial_records" className="text-sm font-medium">
                      Keeps Financial Records
                    </label>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Financial Literacy Score (0-100)
                    </label>
                    <Input
                      type="number"
                      name="financial_literacy_score"
                      value={formData.financial_literacy_score}
                      onChange={handleChange}
                      min="0"
                      max="100"
                      placeholder="70"
                    />
                  </div>
                </div>
              </div>

              {error && (
                <div className="bg-destructive/10 text-destructive text-sm px-4 py-3 rounded">
                  {error}
                </div>
              )}

              <div className="flex gap-4">
                <Button type="submit" disabled={loading} className="flex-1">
                  {loading ? "Creating..." : "Create Borrower"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push("/borrowers")}
                  disabled={loading}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
