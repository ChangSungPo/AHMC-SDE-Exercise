from datetime import datetime, timezone
from bson import ObjectId
from typing import List, Optional, Dict, Any
from ..database import get_revisions_collection
from ..agents.head_agent import HeadAgent
from ..agents.schemas import FinalAssessmentSchema


class RevisionService:
    def __init__(self) -> None:
        self.head_agent = HeadAgent()

    def _format_id(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        doc["id"] = str(doc["_id"])
        return doc

    def analyze(self, raw_note: str) -> FinalAssessmentSchema:
        return self.head_agent.process_unstructured_note(raw_note)

    def create(
        self,
        raw_note: str,
        machine_output: FinalAssessmentSchema,
        user_output: FinalAssessmentSchema,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        is_edited = machine_output.model_dump() != user_output.model_dump()

        new_document = {
            "raw_note": raw_note,
            "machine_output": machine_output.model_dump(),
            "user_output": user_output.model_dump(),
            "is_edited": is_edited,
            "created_at": now,
            "updated_at": now,
        }

        collection = get_revisions_collection()
        result = collection.insert_one(new_document)

        inserted_doc = collection.find_one({"_id": result.inserted_id})

        if inserted_doc is None:
            raise ValueError(
                "[Database Critical Error] Failed to retrieve or format the "
                "new inserted revision document."
            )

        return self._format_id(inserted_doc)

    def get_summary_list(self) -> List[Dict[str, Any]]:
        collection = get_revisions_collection()

        cursor = collection.find(
            {},
            {
                "_id": 1,
                "is_edited": 1,
                "created_at": 1,
                "machine_output.chief_complaint": 1,
                "machine_output.disposition_recommendation": 1,
                "user_output.chief_complaint": 1,
                "user_output.disposition_recommendation": 1,
            },
        ).sort("created_at", -1)

        summaries = []
        for doc in cursor:
            is_edited = doc.get("is_edited", False)
            user_out = doc.get("user_output")
            mach_out = doc.get("machine_output")

            # Correctly extract the active layer
            active_output = user_out if is_edited and user_out else mach_out

            if active_output:
                summaries.append(
                    {
                        "id": str(doc["_id"]),
                        "chief_complaint": active_output.get("chief_complaint", ""),
                        "disposition_recommendation": active_output.get("disposition_recommendation", "Unknown"),
                        "is_edited": is_edited,
                        "created_at": doc.get("created_at"),
                    }
                )
        return summaries

    def get_detail_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(case_id):
            return None

        collection = get_revisions_collection()
        doc = collection.find_one({"_id": ObjectId(case_id)})

        if doc is None:
            return None

        return self._format_id(doc)

    def save_human_edits(
        self, case_id: str, updated_assessment: FinalAssessmentSchema
    ) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(case_id):
            return None

        collection = get_revisions_collection()
        now = datetime.now(timezone.utc)

        update_op = {
            "$set": {
                "user_output": updated_assessment.model_dump(),
                "is_edited": True,
                "updated_at": now,
            }
        }

        result = collection.update_one({"_id": ObjectId(case_id)}, update_op)
        if result.matched_count == 0:
            return None

        updated_doc = collection.find_one({"_id": ObjectId(case_id)})

        if updated_doc is None:
            raise RuntimeError(
                f"[Database Integrity Critical Error] Revision record {case_id} "
                f"was successfully mutated but vanished during verification lookup."
            )

        return self._format_id(updated_doc)

    def purge_case(self, case_id: str) -> bool:
        if not ObjectId.is_valid(case_id):
            return False

        collection = get_revisions_collection()
        result = collection.delete_one({"_id": ObjectId(case_id)})
        return result.deleted_count > 0


revision_service = RevisionService()
