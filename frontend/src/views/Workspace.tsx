import React, { useEffect, useState } from "react";
import { revisionService } from "../service/api";
import type { FinalAssessment } from "../types/clinical";
import { styles } from "./Workspace.styles";

interface WorkspaceProps {
  caseId: string | null;
  preSaveRawNote: string;
  preSaveInference: FinalAssessment | null;
  onSaveSuccess: () => void;
  onCancel: () => void;
}

export const Workspace: React.FC<WorkspaceProps> = ({
  caseId,
  preSaveRawNote,
  preSaveInference,
  onSaveSuccess,
  onCancel,
}) => {
  const [rawNote, setRawNote] = useState<string>("");
  const [machineOutput, setMachineOutput] = useState<FinalAssessment | null>(null);
  const [editedFields, setEditedFields] = useState<FinalAssessment | null>(null);

  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeWorkspace = async () => {
      try {
        setLoading(true);
        if (caseId) {
          const doc = await revisionService.getCaseById(caseId);
          setRawNote(doc.raw_note);
          setMachineOutput(doc.machine_output);
          setEditedFields(doc.user_output ? doc.user_output : doc.machine_output);
          setIsEditing(false);
        } else {
          if (!preSaveInference) throw new Error("Missing unpersisted AI core payload.");
          setRawNote(preSaveRawNote);
          setMachineOutput(preSaveInference);
          setEditedFields(preSaveInference);
          setIsEditing(true);
        }
        setError(null);
      } catch (err) {
        console.error("Workspace mount sync barrier error:", err);
        setError("Failed to lock clinical context. Return to dashboard ledger.");
      } finally {
        setLoading(false);
      }
    };

    initializeWorkspace();
  }, [caseId, preSaveRawNote, preSaveInference]);

  const checkIsModified = (field: keyof FinalAssessment): boolean => {
    if (!editedFields || !machineOutput) return false;
    if (Array.isArray(editedFields[field])) {
      return JSON.stringify(editedFields[field]) !== JSON.stringify(machineOutput[field]);
    }
    return editedFields[field] !== machineOutput[field];
  };

  const handleFieldChange = (field: keyof FinalAssessment, value: unknown) => {
    if (!editedFields) return;
    setEditedFields({ ...editedFields, [field]: value });
  };

  const handleSave = async () => {
    if (!editedFields || !machineOutput) return;
    try {
      setLoading(true);
      if (caseId) {
        await revisionService.updateCase(caseId, editedFields);
      } else {
        await revisionService.createCase(rawNote, machineOutput, editedFields);
      }
      onSaveSuccess();
    } catch (err) {
      console.error("Workspace transaction replication crash:", err);
      setError("Database atomic commit rejected. Check backing container nodes.");
      setLoading(false);
    }
  };

  if (loading) return <div style={styles.centerState}>⏳ Mapping Matrix Streams...</div>;
  if (error || !editedFields || !machineOutput) {
    return (
      <div style={{ ...styles.centerState, borderColor: "#ef4444" }}>
        <div style={{ fontSize: "1.2rem", color: "#f87171" }}>🚨 Workspace Interrupted</div>
        <p>{error}</p>
        <button onClick={onCancel} style={styles.buttonSecondary}>Return Home</button>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Action Header */}
      <div style={styles.actionBar}>
        <div style={styles.titleGroup}>
          <h2 style={styles.title}>Clinical Audit Workspace</h2>
          <span style={styles.modeBadge}>
            {caseId ? `ARCHIVE REF: ${caseId.slice(-6).toUpperCase()}` : "UNSAVED LIVE INFERENCE DRAFT"}
          </span>
        </div>
        <div style={styles.btnGroup}>
          <button onClick={onCancel} style={styles.buttonSecondary}>Cancel</button>
          {caseId && !isEditing && (
            <button onClick={() => setIsEditing(true)} style={styles.buttonAccent}>✏️ Edit Evaluation</button>
          )}
          {isEditing && (
            <button onClick={handleSave} style={styles.buttonPrimary}>💾 Save Changes</button>
          )}
        </div>
      </div>

      <div style={styles.splitLayout}>
        {/* Left Viewport */}
        <div style={styles.panel}>
          <h3 style={styles.panelTitle}>Raw Clinical Intake Documentation</h3>
          <div style={styles.rawViewer}>{rawNote}</div>
        </div>

        {/* Right Viewport */}
        <div style={{ ...styles.panel, overflowY: "auto" }}>
          <h3 style={styles.panelTitle}>Structured Structured Audit Matrix</h3>

          {/* 1. Chief Complaint */}
          <div style={styles.fieldBlock}>
            <div style={styles.labelRow}>
              <label style={styles.fieldLabel}>1. Chief Complaint</label>
              {!isEditing && !checkIsModified("chief_complaint") && (
                <span style={styles.baselineBadge}>✓ Kept AI Revised</span>
              )}
            </div>
            
            {(isEditing || checkIsModified("chief_complaint")) && (
              <div style={styles.versionRow}>
                <div style={styles.versionLabelRow}>🤖 <span>AI Revised</span></div>
                <div style={styles.staticVal}>{machineOutput.chief_complaint}</div>
              </div>
            )}
            
            <div style={styles.versionRow}>
              {!isEditing && !checkIsModified("chief_complaint") ? (
                <div style={styles.staticVal}>{editedFields.chief_complaint}</div>
              ) : (
                <>
                  <div style={styles.versionLabelRow}>✍️ <span>User Update</span></div>
                  {isEditing ? (
                    <input
                      style={styles.inputVal}
                      value={editedFields.chief_complaint}
                      onChange={(e) => handleFieldChange("chief_complaint", e.target.value)}
                    />
                  ) : (
                    <div style={styles.staticVal}>{editedFields.chief_complaint}</div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* 2. HPI Summary */}
          <div style={styles.fieldBlock}>
            <div style={styles.labelRow}>
              <label style={styles.fieldLabel}>2. HPI Summary</label>
              {!isEditing && !checkIsModified("hpi_summary") && (
                <span style={styles.baselineBadge}>✓ Kept AI Revised</span>
              )}
            </div>

            {(isEditing || checkIsModified("hpi_summary")) && (
              <div style={styles.versionRow}>
                <div style={styles.versionLabelRow}>🤖 <span>AI Revised</span></div>
                <div style={{ ...styles.staticVal, whiteSpace: "pre-wrap" }}>{machineOutput.hpi_summary}</div>
              </div>
            )}

            <div style={styles.versionRow}>
              {!isEditing && !checkIsModified("hpi_summary") ? (
                <div style={{ ...styles.staticVal, whiteSpace: "pre-wrap" }}>{editedFields.hpi_summary}</div>
              ) : (
                <>
                  <div style={styles.versionLabelRow}>✍️ <span>User Update</span></div>
                  {isEditing ? (
                    <textarea
                      style={{ ...styles.inputVal, height: "80px", resize: "vertical" }}
                      value={editedFields.hpi_summary}
                      onChange={(e) => handleFieldChange("hpi_summary", e.target.value)}
                    />
                  ) : (
                    <div style={{ ...styles.staticVal, whiteSpace: "pre-wrap" }}>{editedFields.hpi_summary}</div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* 3. Revised HPI */}
          <div style={styles.fieldBlock}>
            <div style={styles.labelRow}>
              <label style={styles.fieldLabel}>3. Revised Chronological HPI</label>
              {!isEditing && !checkIsModified("revised_hpi") && (
                <span style={styles.baselineBadge}>✓ Kept AI Revised</span>
              )}
            </div>

            {(isEditing || checkIsModified("revised_hpi")) && (
              <div style={styles.versionRow}>
                <div style={styles.versionLabelRow}>🤖 <span>AI Revised</span></div>
                <div style={{ ...styles.staticVal, whiteSpace: "pre-wrap" }}>{machineOutput.revised_hpi}</div>
              </div>
            )}

            <div style={styles.versionRow}>
              {!isEditing && !checkIsModified("revised_hpi") ? (
                <div style={{ ...styles.staticVal, whiteSpace: "pre-wrap" }}>{editedFields.revised_hpi}</div>
              ) : (
                <>
                  <div style={styles.versionLabelRow}>✍️ <span>User Update</span></div>
                  {isEditing ? (
                    <textarea
                      style={{ ...styles.inputVal, height: "80px", resize: "vertical" }}
                      value={editedFields.revised_hpi}
                      onChange={(e) => handleFieldChange("revised_hpi", e.target.value)}
                    />
                  ) : (
                    <div style={{ ...styles.staticVal, whiteSpace: "pre-wrap" }}>{editedFields.revised_hpi}</div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* 4. Key Findings */}
          <div style={styles.fieldBlock}>
            <div style={styles.labelRow}>
              <label style={styles.fieldLabel}>4. Key Medical Findings (One per line)</label>
              {!isEditing && !checkIsModified("key_findings") && (
                <span style={styles.baselineBadge}>✓ Kept AI Revised</span>
              )}
            </div>

            {(isEditing || checkIsModified("key_findings")) && (
              <div style={styles.versionRow}>
                <div style={styles.versionLabelRow}>🤖 <span>AI Revised</span></div>
                <div style={styles.staticVal}>
                  {machineOutput.key_findings.map((f, i) => <div key={i}>• {f}</div>)}
                </div>
              </div>
            )}

            <div style={styles.versionRow}>
              {!isEditing && !checkIsModified("key_findings") ? (
                <div style={styles.staticVal}>
                  {editedFields.key_findings.map((f, i) => <div key={i}>• {f}</div>)}
                </div>
              ) : (
                <>
                  <div style={styles.versionLabelRow}>✍️ <span>User Update</span></div>
                  {isEditing ? (
                    <textarea
                      style={{ ...styles.inputVal, height: "80px", resize: "vertical" }}
                      value={editedFields.key_findings.join("\n")}
                      onChange={(e) => handleFieldChange("key_findings", e.target.value.split("\n"))}
                    />
                  ) : (
                    <div style={styles.staticVal}>
                      {editedFields.key_findings.map((f, i) => <div key={i}>• {f}</div>)}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* 5. Suspected Conditions */}
          <div style={styles.fieldBlock}>
            <div style={styles.labelRow}>
              <label style={styles.fieldLabel}>5. Suspected Diagnoses (One per line)</label>
              {!isEditing && !checkIsModified("suspected_conditions") && (
                <span style={styles.baselineBadge}>✓ Kept AI Revised</span>
              )}
            </div>

            {(isEditing || checkIsModified("suspected_conditions")) && (
              <div style={styles.versionRow}>
                <div style={styles.versionLabelRow}>🤖 <span>AI Revised</span></div>
                <div style={styles.staticVal}>
                  {machineOutput.suspected_conditions.map((c, i) => <div key={i}>• {c}</div>)}
                </div>
              </div>
            )}

            <div style={styles.versionRow}>
              {!isEditing && !checkIsModified("suspected_conditions") ? (
                <div style={styles.staticVal}>
                  {editedFields.suspected_conditions.map((c, i) => <div key={i}>• {c}</div>)}
                </div>
              ) : (
                <>
                  <div style={styles.versionLabelRow}>✍️ <span>User Update</span></div>
                  {isEditing ? (
                    <textarea
                      style={{ ...styles.inputVal, height: "80px", resize: "vertical" }}
                      value={editedFields.suspected_conditions.join("\n")}
                      onChange={(e) => handleFieldChange("suspected_conditions", e.target.value.split("\n"))}
                    />
                  ) : (
                    <div style={styles.staticVal}>
                      {editedFields.suspected_conditions.map((c, i) => <div key={i}>• {c}</div>)}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* 6. Uncertainties or Missing Info */}
          <div style={styles.fieldBlock}>
            <div style={styles.labelRow}>
              <label style={styles.fieldLabel}>6. Uncertainties & Missing Information</label>
              {!isEditing && !checkIsModified("uncertainties_or_missing_info") && (
                <span style={styles.baselineBadge}>✓ Kept AI Revised</span>
              )}
            </div>

            {(isEditing || checkIsModified("uncertainties_or_missing_info")) && (
              <div style={styles.versionRow}>
                <div style={styles.versionLabelRow}>🤖 <span>AI Revised</span></div>
                <div style={{ ...styles.staticVal, whiteSpace: "pre-wrap" }}>{machineOutput.uncertainties_or_missing_info}</div>
              </div>
            )}

            <div style={styles.versionRow}>
              {!isEditing && !checkIsModified("uncertainties_or_missing_info") ? (
                <div style={{ ...styles.staticVal, whiteSpace: "pre-wrap" }}>{editedFields.uncertainties_or_missing_info}</div>
              ) : (
                <>
                  <div style={styles.versionLabelRow}>✍️ <span>User Update</span></div>
                  {isEditing ? (
                    <textarea
                      style={{ ...styles.inputVal, height: "80px", resize: "vertical" }}
                      value={editedFields.uncertainties_or_missing_info}
                      onChange={(e) => handleFieldChange("uncertainties_or_missing_info", e.target.value)}
                    />
                  ) : (
                    <div style={{ ...styles.staticVal, whiteSpace: "pre-wrap" }}>{editedFields.uncertainties_or_missing_info}</div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* 7. Disposition Recommendation */}
          <div style={styles.fieldBlock}>
            <div style={styles.labelRow}>
              <label style={styles.fieldLabel}>7. Final Disposition Recommendation</label>
              {!isEditing && !checkIsModified("disposition_recommendation") && (
                <span style={styles.baselineBadge}>✓ Kept AI Revised</span>
              )}
            </div>

            {(isEditing || checkIsModified("disposition_recommendation")) && (
              <div style={styles.versionRow}>
                <div style={styles.versionLabelRow}>🤖 <span>AI Revised</span></div>
                <div style={styles.staticVal}>{machineOutput.disposition_recommendation}</div>
              </div>
            )}

            <div style={styles.versionRow}>
              {!isEditing && !checkIsModified("disposition_recommendation") ? (
                <div style={styles.staticVal}>{editedFields.disposition_recommendation}</div>
              ) : (
                <>
                  <div style={styles.versionLabelRow}>✍️ <span>User Update</span></div>
                  {isEditing ? (
                    <select
                      style={styles.selectVal}
                      value={editedFields.disposition_recommendation}
                      onChange={(e) => handleFieldChange("disposition_recommendation", e.target.value)}
                    >
                      <option value="Admit">Admit</option>
                      <option value="Observe">Observe</option>
                      <option value="Discharge">Discharge</option>
                      <option value="Unknown">Unknown</option>
                    </select>
                  ) : (
                    <div style={styles.staticVal}>{editedFields.disposition_recommendation}</div>
                  )}
                </>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};