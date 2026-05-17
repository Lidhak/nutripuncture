import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import {
  Activity,
  Brain,
  FileText,
  Layers3,
  Link2,
  Plus,
  Save,
  Search,
  Sparkles,
  Tags,
  Trash2,
  Upload,
} from "lucide-react";
import { API_URL, ReferenceItem, ReferencePayload, api } from "./lib/api";
import { Badge, Button, IconButton, Input, Panel, Textarea } from "./components/ui";
import { cn } from "./lib/utils";

const emptyForm: ReferencePayload = {
  title: "",
  category: "",
  description: "",
  numeric_refs: "",
  subcategories: [],
  tags: [],
  associations: [],
  notes: "",
};

function splitList(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function joinList(values: string[]) {
  return values.join(", ");
}

export function App() {
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<ReferenceItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [mode, setMode] = useState<"focus" | "admin">("focus");
  const [form, setForm] = useState<ReferencePayload>(emptyForm);
  const [status, setStatus] = useState("Pret");
  const [isLoading, setIsLoading] = useState(true);

  const selected = useMemo(
    () => items.find((item) => item.id === selectedId) ?? items[0],
    [items, selectedId],
  );

  useEffect(() => {
    const handle = window.setTimeout(async () => {
      setIsLoading(true);
      try {
        const data = query.trim() ? await api.search(query) : await api.list();
        setItems(data);
        if (!selectedId && data[0]) setSelectedId(data[0].id);
        if (selectedId && !data.some((item) => item.id === selectedId) && data[0]) setSelectedId(data[0].id);
      } catch (error) {
        setStatus("API indisponible");
      } finally {
        setIsLoading(false);
      }
    }, 90);
    return () => window.clearTimeout(handle);
  }, [query]);

  useEffect(() => {
    if (mode === "admin" && selected) {
      setForm({
        title: selected.title,
        category: selected.category,
        description: selected.description,
        numeric_refs: selected.numeric_refs,
        subcategories: selected.subcategories,
        tags: selected.tags,
        associations: selected.associations,
        notes: selected.notes,
      });
    }
  }, [mode, selected?.id]);

  async function refresh(nextSelectedId?: number) {
    const data = query.trim() ? await api.search(query) : await api.list();
    setItems(data);
    if (nextSelectedId) setSelectedId(nextSelectedId);
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setStatus("Enregistrement...");
    const payload = { ...form };
    try {
      const saved = selected && mode === "admin" ? await api.update(selected.id, payload) : await api.create(payload);
      await refresh(saved.id);
      setStatus("Fiche enregistree");
    } catch {
      setStatus("Erreur enregistrement");
    }
  }

  async function createNew() {
    setForm(emptyForm);
    setSelectedId(null);
    setMode("admin");
  }

  async function removeSelected() {
    if (!selected) return;
    setStatus("Suppression...");
    await api.remove(selected.id);
    setSelectedId(null);
    await refresh();
    setStatus("Fiche supprimee");
  }

  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setStatus("OCR en cours...");
    try {
      await api.upload(file, selected?.id);
      await refresh(selected?.id);
      setStatus("Document indexe");
    } catch {
      setStatus("Upload impossible");
    }
  }

  return (
    <main className="min-h-screen p-4 text-slate-900 md:p-6">
      <div className="mx-auto grid max-w-[1500px] gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="rounded-lg border border-slate-200 bg-white/86 p-4 shadow-panel backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white shadow-glow">
              <Activity size={20} />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-950">Nutripuncture Desk</p>
              <p className="text-xs text-slate-500">Cabinet local offline</p>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-2">
            <button
              className={cn(
                "rounded-md border px-3 py-2 text-sm font-medium transition",
                mode === "focus" ? "border-blue-200 bg-blue-50 text-blue-700" : "border-slate-200 text-slate-600",
              )}
              onClick={() => setMode("focus")}
            >
              Recherche
            </button>
            <button
              className={cn(
                "rounded-md border px-3 py-2 text-sm font-medium transition",
                mode === "admin" ? "border-blue-200 bg-blue-50 text-blue-700" : "border-slate-200 text-slate-600",
              )}
              onClick={() => setMode("admin")}
            >
              Admin
            </button>
          </div>

          <div className="mt-6 space-y-3">
            <Metric label="Fiches" value={items.length.toString()} />
            <Metric label="Index" value="SQLite FTS5" />
            <Metric label="Statut" value={status} />
          </div>

          <Button className="mt-6 w-full border-blue-200 bg-blue-600 text-white hover:bg-blue-700 hover:text-white" onClick={createNew}>
            <Plus size={16} />
            Nouvelle fiche
          </Button>
        </aside>

        <section className="space-y-4">
          <Panel className="overflow-hidden bg-white/92 backdrop-blur">
            <div className="border-b border-slate-100 p-5">
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase text-blue-600">
                    <Sparkles size={14} />
                    Recherche therapeutique instantanee
                  </div>
                  <h1 className="mt-2 text-2xl font-semibold tracking-normal text-slate-950 md:text-3xl">
                    Retrouver une reference en quelques secondes
                  </h1>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <span className="h-2 w-2 rounded-full bg-emerald-500" />
                  100% local
                </div>
              </div>
              <div className="relative mt-5">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={22} />
                <Input
                  className="h-16 rounded-lg border-slate-200 bg-slate-50 pl-12 text-lg shadow-inner focus:bg-white"
                  autoFocus
                  placeholder="Début de code, organe, fiche, tag... ex: 31 17 34, foie, atlas, amygdale"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                />
              </div>
            </div>

            <div className="grid min-h-[640px] lg:grid-cols-[370px_minmax(0,1fr)]">
              <div className="border-b border-slate-100 lg:border-b-0 lg:border-r">
                <div className="flex items-center justify-between px-4 py-3">
                  <p className="text-sm font-semibold text-slate-700">Resultats</p>
                  <p className="text-xs text-slate-400">{isLoading ? "Indexation..." : `${items.length} fiches`}</p>
                </div>
                <div className="scrollbar-thin max-h-[590px] space-y-2 overflow-y-auto p-3">
                  {items.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setSelectedId(item.id)}
                      className={cn(
                        "w-full rounded-lg border p-4 text-left transition hover:border-blue-200 hover:bg-blue-50/60",
                        selected?.id === item.id ? "border-blue-200 bg-blue-50 shadow-glow" : "border-slate-200 bg-white",
                      )}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h2 className="text-sm font-semibold text-slate-950">{item.title}</h2>
                          <p className="mt-1 text-xs text-slate-500">{item.category}</p>
                        </div>
                        {item.numeric_refs && <Badge tone="blue">{item.numeric_refs}</Badge>}
                      </div>
                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {item.tags.slice(0, 4).map((tag) => (
                          <Badge key={tag}>{tag}</Badge>
                        ))}
                      </div>
                      {item.match_context && (
                        <p className="mt-3 line-clamp-2 rounded-md bg-white/70 px-2 py-1.5 text-xs leading-5 text-slate-500">
                          {item.match_context}
                        </p>
                      )}
                    </button>
                  ))}
                </div>
              </div>

              <div className="min-w-0 bg-gradient-to-b from-white to-slate-50/80">
                {mode === "admin" ? (
                  <AdminPanel
                    form={form}
                    setForm={setForm}
                    selected={selected}
                    onSubmit={submit}
                    onDelete={removeSelected}
                    onUpload={upload}
                  />
                ) : (
                  <ReferenceView selected={selected} />
                )}
              </div>
            </div>
          </Panel>
        </section>
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 truncate text-sm font-semibold text-slate-800">{value}</p>
    </div>
  );
}

function ReferenceView({ selected }: { selected?: ReferenceItem }) {
  if (!selected) {
    return <div className="p-8 text-sm text-slate-500">Aucune fiche selectionnee.</div>;
  }

  return (
    <article className="animate-enter p-5 md:p-7">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <Badge tone="blue">{selected.category}</Badge>
          <h2 className="mt-4 text-3xl font-semibold tracking-normal text-slate-950">{selected.title}</h2>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
            {selected.description || "Aucune description renseignee pour cette reference."}
          </p>
        </div>
        {selected.numeric_refs && (
          <div className="rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-right">
            <p className="text-xs font-medium uppercase text-blue-500">Codes</p>
            <p className="mt-1 text-lg font-semibold text-blue-800">{selected.numeric_refs}</p>
          </div>
        )}
      </div>

      <div className="mt-8 grid gap-4 xl:grid-cols-3">
        <InfoBlock icon={<Tags size={18} />} title="Tags">
          <div className="flex flex-wrap gap-2">
            {selected.tags.map((tag) => (
              <Badge key={tag}>{tag}</Badge>
            ))}
          </div>
        </InfoBlock>
        <InfoBlock icon={<Link2 size={18} />} title="Associations">
          <List values={selected.associations} />
        </InfoBlock>
        <InfoBlock icon={<Layers3 size={18} />} title="Sous-categories">
          <List values={selected.subcategories} />
        </InfoBlock>
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <InfoBlock icon={<Brain size={18} />} title="Notes praticien">
          <p className="text-sm leading-6 text-slate-600">{selected.notes || "Notes libres a completer pendant la consultation."}</p>
        </InfoBlock>
        <InfoBlock icon={<FileText size={18} />} title="Documents et OCR">
          {selected.documents.length === 0 ? (
            <p className="text-sm text-slate-500">Aucun document associe.</p>
          ) : (
            <div className="space-y-3">
              {selected.documents.map((doc) => (
                <a
                  key={doc.id}
                  className="block rounded-md border border-slate-200 bg-white p-3 text-sm transition hover:border-blue-200 hover:bg-blue-50"
                  href={`${API_URL}${doc.stored_path}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  {doc.mime_type.startsWith("image/") && (
                    <img
                      className="mb-3 h-48 w-full rounded-md border border-slate-100 object-contain bg-slate-50"
                      src={`${API_URL}${doc.stored_path}`}
                      alt={doc.filename}
                      loading="lazy"
                    />
                  )}
                  <span className="font-medium text-slate-800">{doc.filename}</span>
                  <span className="mt-1 block line-clamp-2 text-xs text-slate-500">{doc.ocr_text || "OCR sans texte extrait"}</span>
                </a>
              ))}
            </div>
          )}
        </InfoBlock>
      </div>
    </article>
  );
}

function InfoBlock({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-800">
        <span className="text-blue-600">{icon}</span>
        {title}
      </div>
      {children}
    </div>
  );
}

function List({ values }: { values: string[] }) {
  if (!values.length) return <p className="text-sm text-slate-500">Aucun element.</p>;
  return (
    <div className="space-y-2">
      {values.map((value) => (
        <div key={value} className="rounded-md border border-slate-100 bg-slate-50 px-3 py-2 text-sm text-slate-700">
          {value}
        </div>
      ))}
    </div>
  );
}

function AdminPanel({
  form,
  setForm,
  selected,
  onSubmit,
  onDelete,
  onUpload,
}: {
  form: ReferencePayload;
  setForm: (form: ReferencePayload) => void;
  selected?: ReferenceItem;
  onSubmit: (event: FormEvent) => void;
  onDelete: () => void;
  onUpload: (event: ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <form className="animate-enter space-y-5 p-5 md:p-7" onSubmit={onSubmit}>
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-950">Administration</h2>
          <p className="mt-1 text-sm text-slate-500">Ajout, modification, upload et indexation OCR.</p>
        </div>
        <div className="flex gap-2">
          {selected && (
            <IconButton type="button" title="Supprimer" onClick={onDelete}>
              <Trash2 size={16} />
            </IconButton>
          )}
          <Button type="submit" className="border-blue-200 bg-blue-600 text-white hover:bg-blue-700 hover:text-white">
            <Save size={16} />
            Enregistrer
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Field label="Titre">
          <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
        </Field>
        <Field label="Categorie">
          <Input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required />
        </Field>
        <Field label="References numeriques">
          <Input value={form.numeric_refs} onChange={(e) => setForm({ ...form, numeric_refs: e.target.value })} placeholder="15 11 05 27 13" />
        </Field>
        <Field label="Tags">
          <Input value={joinList(form.tags)} onChange={(e) => setForm({ ...form, tags: splitList(e.target.value) })} placeholder="microbiote, intestin" />
        </Field>
        <Field label="Associations">
          <Input
            value={joinList(form.associations)}
            onChange={(e) => setForm({ ...form, associations: splitList(e.target.value) })}
            placeholder="cerveau enterique, commande limbique"
          />
        </Field>
        <Field label="Sous-categories">
          <Input
            value={joinList(form.subcategories)}
            onChange={(e) => setForm({ ...form, subcategories: splitList(e.target.value) })}
            placeholder="atlas-axis, sacrum"
          />
        </Field>
      </div>

      <Field label="Description">
        <Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
      </Field>
      <Field label="Notes">
        <Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
      </Field>

      <div className="rounded-lg border border-dashed border-blue-200 bg-blue-50/50 p-5">
        <label className="flex cursor-pointer flex-col items-center justify-center gap-2 text-center text-sm text-blue-700">
          <Upload size={22} />
          <span className="font-semibold">Uploader une image ou un PDF pour OCR et indexation</span>
          <input className="hidden" type="file" accept="image/*,.pdf" onChange={onUpload} />
        </label>
      </div>
    </form>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block space-y-2">
      <span className="text-xs font-semibold uppercase text-slate-500">{label}</span>
      {children}
    </label>
  );
}
