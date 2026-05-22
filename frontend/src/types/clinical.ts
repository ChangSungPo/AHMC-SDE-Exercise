export type ViewMode = "dashboard" | "ingestion" | "workspace";

export interface FinalAssessment {
  chief_complaint: string;
  hpi_summary: string;
  key_findings: string[];
  suspected_conditions: string[];
  disposition_recommendation: "Admit" | "Observe" | "Discharge" | "Unknown";
  uncertainties_or_missing_info: string;
  revised_hpi: string;
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