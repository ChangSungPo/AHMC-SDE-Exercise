import React, { useEffect, useState } from "react";
import { revisionService } from "../service/api";
import { styles } from "./Dashboard.styles";

interface CaseSummary {
  id: string;
  chief_complaint: string;
  disposition_recommendation: string;
  is_edited: boolean;
  created_at: string;
}

interface DashboardProps {
  onSelectCase: (id: string) => void;
  onCreateClick: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onSelectCase}) => {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        setLoading(true);
        const data = await revisionService.getSummaryList();
        setCases(data);
        setError(null);
      } catch (err) {
        console.error("Failed to sync with clinical database:", err);
        setError("Unable to sync database matrix. Ensure backend container engine is live.");
      } finally {
        setLoading(false);
      }
    };

    fetchCases();
  }, []);

  if (loading) {
    return (
      <div style={styles.centerState}>
        <div style={{ fontSize: "1.2rem", marginBottom: "0.5rem" }}>⏳ Syncing Records...</div>
        <p>Connecting to Multi-Agent historical storage database.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ ...styles.centerState, borderColor: "#ef4444" }}>
        <div style={{ fontSize: "1.2rem", color: "#f87171", marginBottom: "0.5rem" }}>🚨 Connection Failed</div>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.headerRow}>
        <h2 style={styles.title}>Revision Note List</h2>
      </div>

      {cases.length === 0 ? (
        <div style={styles.centerState}>
          <p style={{ margin: 0 }}>No active clinical reviews indexed. Click "New Audit Case" to ingest the first raw record.</p>
        </div>
      ) : (
        <div style={styles.listContainer}>
          {cases.map((item, index) => (
            <div
              key={item.id}
              style={{
                ...styles.listRow,
                borderBottom: index === cases.length - 1 ? "none" : styles.listRow.borderBottom,
              }}
              onClick={() => onSelectCase(item.id)}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#1e293b")}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#0f172a")}
            >
              {/* Left Side: Temporal data and primary clinical complaint */}
              <div style={styles.leftSection}>
                <span style={styles.dateText}>
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
                <h4 style={styles.complaintText}>{item.chief_complaint}</h4>
              </div>

              {/* Right Side: Recommendation metrics and system audit status badges */}
              <div style={styles.rightSection}>
                <div style={styles.recContainer}>
                  Recommendataion: <span style={styles.recommendation}>{item.disposition_recommendation}</span>
                </div>
                <span
                  style={{
                    ...styles.badgeBase,
                    ...(item.is_edited ? styles.auditedBadge : styles.aiOnlyBadge),
                  }}
                >
                  {item.is_edited ? "✓ Audited" : "🤖 AI Only"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};