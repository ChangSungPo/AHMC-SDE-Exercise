import { useState } from "react";
import { Navbar } from "./components/navbar/Navbar";
import { Dashboard } from "./views/Dashboard";
import type { FinalAssessment, ViewMode } from "./types/clinical";
import { Ingestion } from "./views/Ingestion";
import { Workspace } from "./views/Workspace";

function App() {
  const [currentView, setCurrentView] = useState<ViewMode>("dashboard");

  const handleCreateClick = () => {
    setCurrentView("ingestion");
  };

  const [preSaveRawNote, setPreSaveRawNote] = useState<string>("");
  const [preSaveInference, setPreSaveInference] = useState<FinalAssessment | null>(null);

  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);

  const handleInferenceComplete = (rawNote: string, inference: FinalAssessment) => {
    setPreSaveRawNote(rawNote);
    setPreSaveInference(inference);
    setCurrentView("workspace"); 
  };

  const handleSelectCase = (caseId: string) => {
    setSelectedCaseId(caseId);
    setPreSaveInference(null); 
    setCurrentView("workspace");
  };

  const handleNavigateHome = () => {
    setSelectedCaseId(null);
    setPreSaveInference(null);
    setPreSaveRawNote("");
    setCurrentView("dashboard");
  };

  return (
    <div>
      <Navbar currentView={currentView} onViewChange={(view) => setCurrentView(view)} />

      <main>
        {currentView === "dashboard" && (
          <Dashboard 
            onSelectCase={handleSelectCase} 
            onCreateClick={handleCreateClick} 
          />
        )}

        {currentView === "ingestion" && (
          <Ingestion onInferenceSuccess={handleInferenceComplete} />
        )}

        {currentView === "workspace" && (
          <div 
          // style={{ padding: "2rem", backgroundColor: "#0f172a", borderRadius: "12px", border: "1px solid #1e293b" }}
          >
            {/* <button onClick={() => setCurrentView("dashboard")}>Back to Dashboard</button> */}
          </div>
        )}

        {currentView === "workspace" && (
          <Workspace
            caseId={selectedCaseId}
            preSaveRawNote={preSaveRawNote}
            preSaveInference={preSaveInference}
            onSaveSuccess={handleNavigateHome}
            onCancel={handleNavigateHome}
          />
        )}
      </main>
    </div>
  );
}

export default App;