import React from "react";

export const styles: { [key: string]: React.CSSProperties } = {
  nav: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#0f172a",
    padding: "0.75rem 2rem",
    borderBottom: "2px solid #1e293b",
    color: "#f8fafc",
    fontFamily: "system-ui, sans-serif",
  },
  brandContainer: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
  },
  logoPulse: {
    width: "10px",
    height: "10px",
    backgroundColor: "#10b981",
    borderRadius: "50%",
    boxShadow: "0 0 8px #10b981",
  },
  brandName: {
    fontSize: "1.1rem",
    fontWeight: 700,
    letterSpacing: "0.5px",
    color: "#f8fafc",
  },
  envTag: {
    fontSize: "0.75rem",
    backgroundColor: "#1e293b",
    padding: "0.2rem 0.5rem",
    borderRadius: "4px",
    color: "#64748b",
  },
  menuGroup: {
    display: "flex",
    gap: "0.5rem",
  },
  navButton: {
    backgroundColor: "transparent",
    border: "none",
    color: "#94a3b8",
    padding: "0.5rem 1rem",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: 600,
    fontSize: "0.9rem",
    transition: "all 0.2s ease",
  },
  activeButton: {
    backgroundColor: "#1e293b",
    color: "#34d399",
    boxShadow: "inset 0 1px 0 0 rgba(255,255,255,0.05)",
  },
};