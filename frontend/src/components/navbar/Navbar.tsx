import React from "react";
import { styles } from "./Navbar.styles";
import type { ViewMode } from "../../types/clinical";

export interface NavbarProps {
  currentView: ViewMode;
  onViewChange: (view: ViewMode) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentView, onViewChange }) => {
  return (
    <nav style={styles.nav}>
      <div style={styles.brandContainer}>
        <div style={styles.logoPulse}></div>
        <span style={styles.brandName}>Multi-Agent Clinical Engine</span>
        <span style={styles.envTag}>2026-v1</span>
      </div>

      <div style={styles.menuGroup}>
        <button
          style={{ ...styles.navButton, ...(currentView === "dashboard" ? styles.activeButton : {}) }}
          onClick={() => onViewChange("dashboard")}
        >
        Dashboard
        </button>
        <button
          style={{ ...styles.navButton, ...(currentView === "ingestion" ? styles.activeButton : {}) }}
          onClick={() => onViewChange("ingestion")}
        >
        New Case
        </button>
      </div>
    </nav>
  );
};