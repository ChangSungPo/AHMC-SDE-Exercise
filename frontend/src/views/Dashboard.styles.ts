import React from "react";

export const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: "flex",
    flexDirection: "column",
    gap: "1.5rem",
  },
  headerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "0.5rem",
  },
  title: {
    fontSize: "1.5rem",
    fontWeight: 700,
    margin: 0,
    color: "#f8fafc",
  },
  createButton: {
    backgroundColor: "#10b981",
    color: "#ffffff",
    border: "none",
    padding: "0.6rem 1.2rem",
    borderRadius: "6px",
    fontWeight: 600,
    cursor: "pointer",
    transition: "background-color 0.2s",
  },
  // 🌟 Changed from grid to vertical list container
  listContainer: {
    display: "flex",
    flexDirection: "column",
    backgroundColor: "#0f172a",
    border: "1px solid #1e293b",
    borderRadius: "8px",
    overflow: "hidden",
  },
  // 🌟 Horizontal row layout for each case
  listRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "1rem 1.5rem",
    borderBottom: "1px solid #1e293b",
    cursor: "pointer",
    transition: "background-color 0.2s",
  },
  leftSection: {
    display: "flex",
    alignItems: "center",
    gap: "1.5rem",
    flex: 1,
  },
  dateText: {
    fontSize: "0.85rem",
    color: "#64748b",
    minWidth: "90px",
  },
  complaintText: {
    fontSize: "0.95rem",
    fontWeight: 600,
    color: "#e2e8f0",
    margin: 0,
  },
  rightSection: {
    display: "flex",
    alignItems: "center",
    gap: "2rem",
  },
  recContainer: {
    fontSize: "0.9rem",
    color: "#94a3b8",
    minWidth: "100px",
  },
  recommendation: {
    fontWeight: 600,
    color: "#38bdf8",
  },
  badgeBase: {
    fontSize: "0.75rem",
    padding: "0.25rem 0.5rem",
    borderRadius: "4px",
    fontWeight: 700,
    whiteSpace: "nowrap",
    textAlign: "center",
    minWidth: "65px",
  },
  auditedBadge: {
    backgroundColor: "rgba(16, 185, 129, 0.1)",
    color: "#34d399",
    border: "1px solid rgba(16, 185, 129, 0.2)",
  },
  aiOnlyBadge: {
    backgroundColor: "rgba(148, 163, 184, 0.1)",
    color: "#94a3b8",
    border: "1px solid rgba(148, 163, 184, 0.2)",
  },
  centerState: {
    textAlign: "center",
    padding: "4rem 2rem",
    backgroundColor: "#0f172a",
    borderRadius: "12px",
    border: "1px solid #1e293b",
    color: "#94a3b8",
  },
};