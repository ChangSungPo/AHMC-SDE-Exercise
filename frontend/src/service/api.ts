import { config } from "../config/config";
import type { FinalAssessment } from "../types/clinical";

export interface CaseSummary {
  id: string;
  chief_complaint: string;
  disposition_recommendation: string;
  is_edited: boolean;
  created_at: string;
}

export interface ClinicalRevisionDocument {
  id: string;
  raw_note: string;
  machine_output: FinalAssessment;
  user_output: FinalAssessment | null;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
}

export const revisionService = {
  async getSummaryList(): Promise<CaseSummary[]> {
    const response = await fetch(`${config.apiBaseUrl}/revisions`);
    
    if (!response.ok) {
      throw new Error(`Network response error: ${response.status}`);
    }
    
    return response.json();
  },

  async analyzeCase(rawNote: string): Promise<FinalAssessment> {
    const response = await fetch(`${config.apiBaseUrl}/revisions/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ raw_note: rawNote }),
    });

    if (!response.ok) {
      throw new Error(`AI analysis engine failed with status: ${response.status}`);
    }

    return response.json();
  },

  async getCaseById(id: string): Promise<ClinicalRevisionDocument> {
    const response = await fetch(`${config.apiBaseUrl}/revisions/${id}`);
    if (!response.ok) throw new Error(`Fetch case details failed: ${response.status}`);
    return response.json();
  },

  async createCase(rawNote: string, machine: FinalAssessment, user: FinalAssessment): Promise<void> {
    const response = await fetch(`${config.apiBaseUrl}/revisions/save`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        raw_note: rawNote,
        machine_output: machine,
        user_output: user,
      }),
    });
    if (!response.ok) throw new Error(`Failed to create clinical record: ${response.status}`);
  },

  async updateCase(id: string, userOutput: FinalAssessment): Promise<void> {
    const response = await fetch(`${config.apiBaseUrl}/revisions/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_output: userOutput }),
    });
    if (!response.ok) throw new Error(`Failed to update clinical revision: ${response.status}`);
  },
};