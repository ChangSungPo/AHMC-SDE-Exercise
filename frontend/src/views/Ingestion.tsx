import React, { useState } from "react";
import { revisionService } from "../service/api";
import type { FinalAssessment } from "../types/clinical";
import { styles } from "./Ingestion.styles";

interface IngestionProps {
  onInferenceSuccess: (rawNote: string, inference: FinalAssessment) => void;
}

export const Ingestion: React.FC<IngestionProps> = ({ onInferenceSuccess }) => {
  const [rawNote, setRawNote] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawNote.trim()) return;

    try {
      setLoading(true);
      setError(null);
      
      const inferenceResult = await revisionService.analyzeCase(rawNote);
      
      onInferenceSuccess(rawNote, inferenceResult);
    } catch (err) {
      console.error("Ingestion ingestion pipeline crash:", err);
      setError("Clinical agent framework encountered an error. Check server logs.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={styles.centerState}>
        <div style={{ fontSize: "1.5rem", marginBottom: "0.75rem" }}>🧠 Orchesterating Multi-Agent Audit...</div>
        <p style={{ margin: 0, color: "#64748b" }}>
          Rewriting clinical context, matching validation matrices, and verifying medical necessity.
        </p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div>
        <h2 style={styles.title}>Paste Unstructured Medical Note</h2>
      </div>

      <form onSubmit={handleSubmit} style={styles.form}>
        {error && <p style={styles.errorText}>🚨 {error}</p>}

        <textarea
          style={styles.textarea}
          placeholder="Enter raw, unstructured medical intake note here..."
          value={rawNote}
          onChange={(e) => setRawNote(e.target.value)}
          disabled={loading}
        />

        <div style={styles.buttonRow}>
          <button
            type="submit"
            style={{
              ...styles.submitButton,
              ...(!rawNote.trim() ? styles.submitButtonDisabled : {}),
            }}
            disabled={!rawNote.trim() || loading}
          >
            ⚡ Launch AI Clinical Audit
          </button>
        </div>
      </form>
    </div>
  );
};