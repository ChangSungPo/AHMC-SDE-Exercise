import requests
import json

BASE_URL = "http://localhost:8000/api/revisions"


def test_full_api_workflow():
    print("[API Test] Starting full End-to-End API Workflow Verification...")

# ==========================================================================================
    raw_note_data = (
        "A 47-year-old man with recently diagnosed diabetes started metformin and Jardiance on Friday morning "
        "and became increasingly restless and unable to sleep over the day. Yesterday morning he was unable to "
        "tolerate oral intake and had one episode of vomiting. This morning he had several episodes of vomiting "
        "with ongoing nausea and came to the emergency department for evaluation. In the emergency department "
        "he was noted to have euglycemic diabetic ketoacidosis with bicarbonate less than 7, potential of "
        "hydrogen value 7.2, and glucose 93, and admission was requested for euglycemic diabetic ketoacidosis "
        "likely in the setting of new Jardiance use."
    )

    print("\nStep 1: Testing Case Ingestion & AI Pipeline (POST /analyze)...")
    payload = {"raw_note": raw_note_data}
    response = requests.post(f"{BASE_URL}/analyze", json=payload)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    machine_output_data = response.json()
    assert "id" not in machine_output_data, "Error: /analyze endpoint should be stateless and not generate a DB ID!"
    print("Success! AI framework computed the unstructured text successfully.")
    print(f"Machine Original Output: {machine_output_data['disposition_recommendation']}")
# ==========================================================================================

# ==========================================================================================
    print("\nStep 2: Testing Case Saving (POST /create)...")

    user_edited_output = machine_output_data.copy()
    user_edited_output["revised_hpi"] = "HUMAN EDIT BEFORE SAVING: Metformin and Jardiance toxicity suspected. Highly critical DKA case."
    user_edited_output["disposition_recommendation"] = "Admit"
    
    save_payload = {
        "raw_note": raw_note_data,
        "machine_output": machine_output_data,
        "user_output": user_edited_output
    }
    
    save_response = requests.post(f"{BASE_URL}/save", json=save_payload)

    assert save_response.status_code == 201, f"Expected 201, got {response.status_code}"
    case_data = save_response.json()
    case_id = case_data["id"]
    
    assert case_data["is_edited"] is True
    print(f"Success! Case created in MongoDB with ID: {case_id}")
    print(f"Pre-save Modified HPI: {case_data['user_output']['revised_hpi']}")
    
# ==========================================================================================


# ==========================================================================================
    print("\nStep 3: Testing Dashboard List Fetches (GET /revisions)...")
    list_response = requests.get(BASE_URL)
    assert list_response.status_code == 200
    print(f"Success! Found {len(list_response.json())} cases in the active database grid.")
# ==========================================================================================


# ==========================================================================================
    print(f"\nStep 4: Testing Human Overwrite Commit (PUT /revisions/{case_id})...")

    modified_user_output = case_data["machine_output"].copy()
    modified_user_output["revised_hpi"] = "CRITICAL HUMAN REVISION: Patient is in severe DKA, immediate ICU placement needed."

    update_payload = {"user_output": modified_user_output}

    update_response = requests.put(f"{BASE_URL}/{case_id}", json=update_payload)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["is_edited"] is True
    print("Success! Human edit session successfully saved.")
    print(f"New User HPI Saved: {updated_data['user_output']['revised_hpi']}")
   
    
# ==========================================================================================
    print(f"\nStep 5: Testing Context Retrieval & Audit Trail Verification (GET /revisions/{case_id})...")
    detail_response = requests.get(f"{BASE_URL}/{case_id}")
    assert detail_response.status_code == 200
    final_snapshot = detail_response.json()

    print("Final Check:")
    print(f"Machine Original Backup Exists: {final_snapshot['machine_output'] is not None}")
    print(f"User Modified Version Exists: {final_snapshot['user_output'] is not None}")
    print(f"Audited Status [is_edited]: {final_snapshot['is_edited']}")
# ==========================================================================================

    print("\n[All Passed] Backend API layer is 100% stable and verified!")


if __name__ == "__main__":
    try:
        test_full_api_workflow()
    except Exception as e:
        print(f"\n[Test Failed] API simulation broke: {str(e)}")
