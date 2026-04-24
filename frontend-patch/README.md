# Frontend Patch Instructions

This folder contains instructions for updating the existing React frontend to work with the new docSmith agentic backend.

## Changes Required

### 1. API Client Updates

Replace your existing API calls with the new endpoints:

```typescript
// API base URL — point to the FastAPI backend
const API_BASE = "http://localhost:8000";

// POST /generate — start a new generation
const response = await fetch(`${API_BASE}/generate`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ url: "https://github.com/user/repo", generation_type: "docs" }),
});
const { id, status } = await response.json();
// Use `id` to subscribe to SSE stream
```

### 2. SSE Stream Connection

Connect to `/stream/{id}` for real-time progress:

```typescript
const eventSource = new EventSource(`http://localhost:8000/stream/${id}`);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case "cloning":
    case "thinking":
    case "reading":
    case "generating":
      // Update progress UI with data.content
      setProgress(data.content);
      break;
    case "stream":
      // Append streaming content to output
      appendOutput(data.content);
      break;
    case "done":
      // Generation complete
      setResult(data.result);
      eventSource.close();
      break;
    case "error":
      // Handle error
      setError(data.content);
      eventSource.close();
      break;
  }
};
```

### 3. Polling Fallback (if SSE fails)

If EventSource doesn't work in your setup, poll `/result/{id}` every 2 seconds:

```typescript
const poll = setInterval(async () => {
  const res = await fetch(`${API_BASE}/result/${id}`);
  const data = await res.json();
  if (data.status === "done" || data.status === "failed") {
    setResult(data.content);
    clearInterval(poll);
  }
}, 2000);
```

### 4. Display Generation Result

```typescript
// GET /result/{id} — fetch completed result
const res = await fetch(`${API_BASE}/result/${id}`);
const data = await res.json();

if (data.content) {
  // Render markdown in UI
  setGeneratedContent(data.content);
}
```

### 5. History Page

```typescript
// GET /history
const res = await fetch(`${API_BASE}/history`);
const history = await res.json();
// Display list with repo_url, generation_type, status, created_at
```

### 6. Regenerate

```typescript
// POST /regenerate/{id}
await fetch(`${API_BASE}/regenerate/${id}`, { method: "POST" });
// Then reconnect to SSE stream
```

## Example React Component

```tsx
import { useState, useEffect } from "react";

export function DocSmithGenerator() {
  const [genId, setGenId] = useState<number | null>(null);
  const [progress, setProgress] = useState("");
  const [output, setOutput] = useState("");
  const [status, setStatus] = useState("");

  const startGeneration = async (url: string, type: string) => {
    const res = await fetch("http://localhost:8000/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, generation_type: type }),
    });
    const { id } = await res.json();
    setGenId(id);
  };

  useEffect(() => {
    if (!genId) return;
    
    const es = new EventSource(`http://localhost:8000/stream/${genId}`);
    es.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "done") {
        setOutput(data.result || output);
        es.close();
      } else if (data.type === "error") {
        setStatus("Error: " + data.content);
        es.close();
      } else if (data.type === "stream") {
        setOutput((prev) => prev + data.content);
      } else {
        setProgress(data.content);
      }
    };
    return () => es.close();
  }, [genId]);

  return (
    <div>
      <p>Progress: {progress}</p>
      <pre>{output}</pre>
    </div>
  );
}
```

## CORS

The backend allows all origins (`allow_origins=["*"]`). Update this in `main.py` for production.

## Environment Variable

Make sure the backend has ``OPENROUTER_API_KEY`` set in the environment before running.