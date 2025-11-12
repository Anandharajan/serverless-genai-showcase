"""Hybrid DynamoDB + local JSON store helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from services.common import env

try:
    import boto3  # type: ignore

except Exception:  # pragma: no cover - boto3 is optional for local tests
    boto3 = None


def _dynamo_table(table_name: str):


    if os.getenv("GENAI_LOCAL_ONLY") == "1":


        return None


    if boto3 is None:


        return None


    try:


        endpoint_url = "http://localhost:4566"


        aws_access_key_id = "test"


        aws_secret_access_key = "test"


        print(f"Creating table resource for table: {table_name} with endpoint: {endpoint_url}")


        resource = boto3.resource("dynamodb",


                                  endpoint_url=endpoint_url,


                                  aws_access_key_id=aws_access_key_id,


                                  aws_secret_access_key=aws_secret_access_key,


                                  region_name=os.environ.get("AWS_REGION", "us-east-1"))


        return resource.Table(table_name)


    except Exception as e:


        print(f"Error creating table resource: {e}")


        return None





class TableStore:


    """Simple convenience wrapper for a DynamoDB table with local fallback."""





    def __init__(self, table_name: str, partition_key: str):


        self.table_name = table_name


        self.partition_key = partition_key


        self._table = _dynamo_table(table_name)


        self._local_path = Path(env.LOCAL_STATE_DIR) / f"{table_name}.json"


        self._local_path.parent.mkdir(parents=True, exist_ok=True)


        if not self._local_path.exists():


            self._local_path.write_text("[]", encoding="utf-8")





    # Public operations --------------------------------------------------


    def put(self, item: Dict[str, Any]) -> Dict[str, Any]:


        if self._table:


            self._table.put_item(Item=item)


        else:


            items = self._read_local()


            items = [i for i in items if i.get(self.partition_key) != item[self.partition_key]]


            items.append(item)


            self._write_local(items)


        return item





    def get(self, value: str) -> Optional[Dict[str, Any]]:


        if self._table:


            resp = self._table.get_item(Key={self.partition_key: value})


            return resp.get("Item")


        items = self._read_local()


        return next((item for item in items if item.get(self.partition_key) == value), None)





    def scan(self) -> List[Dict[str, Any]]:


        print(f"Scanning table: {self.table_name} with table object: {self._table}")


        if self._table:


            resp = self._table.scan()


            return resp.get("Items", [])


        return self._read_local()

    def remove(self, value: str) -> None:
        if self._table:
            self._table.delete_item(Key={self.partition_key: value})
            return
        items = [item for item in self._read_local() if item.get(self.partition_key) != value]
        self._write_local(items)

    # Local persistence --------------------------------------------------
    def _read_local(self) -> List[Dict[str, Any]]:
        data = self._local_path.read_text(encoding="utf-8")
        if not data:
            return []
        return json.loads(data)

    def _write_local(self, data: List[Dict[str, Any]]) -> None:
        self._local_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# Concrete stores -----------------------------------------------------------


class PromptHistoryStore(TableStore):
    def __init__(self):
        super().__init__(env.PROMPT_TABLE, partition_key="requestId")

    def log_prompt(self, *, user_id: str, prompt: str, response: str, model_id: str) -> Dict[str, Any]:
        item = {
            "requestId": str(uuid4()),
            "userKey": f"{user_id}#{env.STAGE}",
            "prompt": prompt,
            "response": response,
            "modelId": model_id,
        }
        return self.put(item)


class ModelMetadataStore(TableStore):
    def __init__(self):
        super().__init__(env.MODEL_TABLE, partition_key="modelId")

    def register_model(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        model = {
            "modelId": payload.get("modelId") or str(uuid4()),
            "provider": payload.get("provider", "mock"),
            "type": payload.get("type", "chat"),
            "costPer1kTokens": float(payload.get("costPer1kTokens", 0.0)),
            "active": payload.get("active", True),
            "meta": payload.get("meta", {}),
        }
        self.put(model)
        return model

    def list_models(self) -> List[Dict[str, Any]]:
        return self.scan()

    def set_active(self, model_id: str) -> Dict[str, Any]:
        models = self.scan()
        for model in models:
            model["active"] = model["modelId"] == model_id
            self.put(model)
        selected = next((m for m in models if m["modelId"] == model_id), None)
        if not selected:
            raise ValueError(f"Unknown model_id {model_id}")
        return selected

    def get_active_model(self) -> str:
        models = self.scan()
        for model in models:
            if model.get("active"):
                return model["modelId"]
        if models:
            return models[0]["modelId"]
        seed = self.register_model({"modelId": env.DEFAULT_MODEL_ID, "provider": "mock"})
        return seed["modelId"]


class AgentLifecycleStore(TableStore):
    def __init__(self):
        super().__init__(env.AGENT_TABLE, partition_key="agentRunId")

    def start_run(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        run = {
            "agentRunId": str(uuid4()),
            "plan": plan,
            "status": "running",
        }
        return self.put(run)

    def complete_run(self, run_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        record = self.get(run_id)
        if not record:
            record = {"agentRunId": run_id}
        record.update({"status": "complete", "result": result})
        return self.put(record)


class RetrievalIndexStore(TableStore):
    def __init__(self):
        super().__init__(env.RETRIEVAL_TABLE, partition_key="docId")

    def upsert_document(self, *, doc_id: str, content: str, metadata: Dict[str, Any] | None = None):
        metadata = metadata or {}
        item = {
            "docId": doc_id,
            "content": content,
            "metadata": metadata,
        }
        return self.put(item)

    def list_documents(self) -> List[Dict[str, Any]]:
        docs = self.scan()
        if not docs:
            # seed with minimal knowledge base
            self.upsert_document(
                doc_id="seed-architecture",
                content="This showcase demonstrates LLM adapters, RAG, and governance controls on AWS SAM.",
                metadata={"tags": ["architecture", "overview"]},
            )
            docs = self.scan()
        return docs

    def top_k(self, limit: int = 4) -> List[Dict[str, Any]]:
        return self.list_documents()[:limit]
