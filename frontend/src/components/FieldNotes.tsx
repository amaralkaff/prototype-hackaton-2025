"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { fieldNotesAPI } from "@/lib/api";

interface FieldNote {
  id: string;
  borrower_id: string;
  loan_id?: string;
  note_text: string;
  note_type: string;
  visit_date?: string;
  field_agent_name?: string;
  nlp_analysis_status: string;
  created_at: string;
}

interface FieldNotesProps {
  borrowerId: string;
  fieldNotes: FieldNote[];
  onNotesChange?: () => void;
}

const NOTE_TYPES = [
  { value: "initial_visit", label: "Initial Visit" },
  { value: "follow_up", label: "Follow-up" },
  { value: "repayment_collection", label: "Repayment Collection" },
  { value: "business_observation", label: "Business Observation" },
  { value: "risk_assessment", label: "Risk Assessment" },
  { value: "general", label: "General" },
];

export default function FieldNotes({ borrowerId, fieldNotes, onNotesChange }: FieldNotesProps) {
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    note_text: "",
    note_type: "initial_visit",
    field_agent_name: "",
    visit_date: new Date().toISOString().split('T')[0],
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (!formData.note_text.trim()) {
        throw new Error("Note text is required");
      }

      await fieldNotesAPI.create({
        borrower_id: borrowerId,
        note_text: formData.note_text,
        note_type: formData.note_type,
        field_agent_name: formData.field_agent_name || undefined,
        visit_date: formData.visit_date || undefined,
      });

      // Reset form
      setFormData({
        note_text: "",
        note_type: "initial_visit",
        field_agent_name: "",
        visit_date: new Date().toISOString().split('T')[0],
      });
      setShowForm(false);

      if (onNotesChange) {
        onNotesChange();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create field note");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (noteId: string) => {
    if (!confirm("Are you sure you want to delete this field note?")) {
      return;
    }

    try {
      await fieldNotesAPI.delete(noteId);

      if (onNotesChange) {
        onNotesChange();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getNoteTypeLabel = (type: string) => {
    return NOTE_TYPES.find(t => t.value === type)?.label || type;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>Field Notes ({fieldNotes.length})</CardTitle>
            <CardDescription>Field agent observations and notes</CardDescription>
          </div>
          <Button onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "+ Add Note"}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Add Note Form */}
        {showForm && (
          <form onSubmit={handleSubmit} className="space-y-4 border rounded-lg p-4 bg-muted/10">
            <div>
              <label className="block text-sm font-medium mb-2">
                Note Type <span className="text-destructive">*</span>
              </label>
              <select
                name="note_type"
                value={formData.note_type}
                onChange={handleChange}
                required
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {NOTE_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Note Text <span className="text-destructive">*</span>
              </label>
              <textarea
                name="note_text"
                value={formData.note_text}
                onChange={handleChange}
                required
                rows={5}
                placeholder="Enter field observations, borrower interactions, business conditions, etc..."
                className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Agent Name</label>
                <Input
                  name="field_agent_name"
                  value={formData.field_agent_name}
                  onChange={handleChange}
                  placeholder="Your name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Visit Date</label>
                <Input
                  type="date"
                  name="visit_date"
                  value={formData.visit_date}
                  onChange={handleChange}
                />
              </div>
            </div>

            {error && (
              <div className="bg-destructive/10 text-destructive text-sm px-4 py-3 rounded">
                {error}
              </div>
            )}

            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "Creating..." : "Create Field Note"}
            </Button>
          </form>
        )}

        {/* Field Notes List */}
        {fieldNotes.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">No field notes recorded</p>
        ) : (
          <div className="space-y-4">
            {fieldNotes.map((note) => (
              <div key={note.id} className="border rounded-lg p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex gap-2">
                    <Badge variant="outline">
                      {getNoteTypeLabel(note.note_type)}
                    </Badge>
                    <Badge variant={note.nlp_analysis_status === 'completed' ? 'default' : 'secondary'}>
                      {note.nlp_analysis_status}
                    </Badge>
                  </div>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDelete(note.id)}
                  >
                    Delete
                  </Button>
                </div>

                <p className="text-sm whitespace-pre-wrap">{note.note_text}</p>

                <div className="flex justify-between items-center text-xs text-muted-foreground pt-2 border-t">
                  <div>
                    {note.field_agent_name && (
                      <span>By {note.field_agent_name} • </span>
                    )}
                    {note.visit_date && (
                      <span>Visit: {new Date(note.visit_date).toLocaleDateString()} • </span>
                    )}
                    <span>Created: {formatDate(note.created_at)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
