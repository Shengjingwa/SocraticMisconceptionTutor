from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from state import SessionMemory
from router import PerceptionResult, RouteDecision
from langgraph.checkpoint.memory import MemorySaver

try:
    serializer = JsonPlusSerializer().with_msgpack_allowlist(
        [SessionMemory, PerceptionResult, RouteDecision]
    )
    ms = MemorySaver(serde=serializer)
    print("Success!")
except Exception as e:
    print("Error:", e)
