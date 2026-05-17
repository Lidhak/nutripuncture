export const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export type ReferenceItem = {
  id: number;
  title: string;
  category: string;
  description: string;
  numeric_refs: string;
  subcategories: string[];
  tags: string[];
  associations: string[];
  notes: string;
  documents: DocumentItem[];
  match_context: string;
};

export type DocumentItem = {
  id: number;
  filename: string;
  stored_path: string;
  mime_type: string;
  ocr_text: string;
  ocr_status: string;
  ocr_engine: string;
  created_at: string;
};

export type UploadResult = {
  document_id: number;
  filename: string;
  stored_path: string;
  ocr_text: string;
  ocr_status: string;
  ocr_engine: string;
  character_count: number;
};

export type ReferencePayload = Omit<ReferenceItem, "id" | "documents" | "match_context">;

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: options?.body instanceof FormData ? undefined : { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export const api = {
  list: () => request<ReferenceItem[]>("/references"),
  search: (q: string) => request<ReferenceItem[]>(`/search?q=${encodeURIComponent(q)}`),
  create: (payload: ReferencePayload) =>
    request<ReferenceItem>("/references", { method: "POST", body: JSON.stringify(payload) }),
  update: (id: number, payload: ReferencePayload) =>
    request<ReferenceItem>(`/references/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  remove: (id: number) => request<{ deleted: boolean }>(`/references/${id}`, { method: "DELETE" }),
  upload: (file: File, referenceId?: number) => {
    const form = new FormData();
    form.append("file", file);
    if (referenceId) form.append("reference_id", String(referenceId));
    return request<UploadResult>("/documents/upload", { method: "POST", body: form });
  },
  updateOcr: (documentId: number, ocrText: string) =>
    request<DocumentItem>(`/documents/${documentId}/ocr`, {
      method: "PUT",
      body: JSON.stringify({ ocr_text: ocrText }),
    }),
};
