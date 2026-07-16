/**
 * MCP SERVER — Screenwriting Reference
 *
 * Stellt Drehbuchtheorie, Beispiel-Screenplays und Treatments
 * über das Model Context Protocol zur Verfügung.
 *
 * Tools:
 *   - search_theory:     Durchsucht Theoriebücher (McKee, Field, Seger, etc.)
 *   - search_screenplays: Durchsucht Drehbücher nach Stichwort oder Technik
 *   - search_treatments:  Durchsucht Treatment-Beispiele
 *   - get_document_excerpt: Liest Ausschnitt aus einem bestimmten Dokument
 *   - list_references:    Zeigt alle verfügbaren Referenzen
 *   - search_all:         Sucht über den gesamten Korpus
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const INDEX_FILE = path.join(__dirname, "index.json");

// ── Index laden ──────────────────────────────────────────────

let index;
try {
  index = JSON.parse(fs.readFileSync(INDEX_FILE, "utf-8"));
} catch (e) {
  console.error("Index nicht gefunden. Erst 'node indexer.js' ausführen.");
  process.exit(1);
}

// ── Suchfunktionen ───────────────────────────────────────────

function searchChunks(query, category = null, maxResults = 5) {
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (terms.length === 0) return [];

  const scored = [];

  for (const chunk of index.chunks) {
    const doc = index.documents[chunk.doc_id];
    if (category && doc.category !== category) continue;

    const textLower = chunk.text.toLowerCase();
    let score = 0;

    for (const term of terms) {
      const regex = new RegExp(term, "gi");
      const matches = textLower.match(regex);
      if (matches) {
        score += matches.length;
      }
    }

    // Bonus für exakte Phrasen-Matches
    const fullQuery = query.toLowerCase();
    if (textLower.includes(fullQuery)) {
      score += terms.length * 3;
    }

    if (score > 0) {
      scored.push({ chunk, doc, score });
    }
  }

  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, maxResults);
}

function formatResults(results) {
  if (results.length === 0) {
    return "Keine Treffer gefunden.";
  }

  return results
    .map((r, i) => {
      const doc = r.doc;
      const chunk = r.chunk;
      const pos = `Chunk ${chunk.chunk_index + 1}/${chunk.total_chunks}`;
      return (
        `--- Treffer ${i + 1} (Score: ${r.score}) ---\n` +
        `Quelle: ${doc.title} [${doc.category}] (${pos})\n` +
        `${doc.is_adaptation ? "[ADAPTION] " : ""}` +
        `\n${chunk.text}\n`
      );
    })
    .join("\n");
}

// ── MCP Server ───────────────────────────────────────────────

const server = new McpServer({
  name: "screenwriting-reference",
  version: "1.0.0",
});

// Tool: search_theory
server.tool(
  "search_theory",
  "Durchsucht Drehbuch-Theoriebücher (Syd Field, Linda Seger, Egri, David Howard, 8-Sequenz-Modell) nach einem Thema oder Begriff. Nutze dies für Fragen zu Dramaturgie, Struktur, Figurenentwicklung, Adaption, Treatment-Format etc.",
  {
    query: z.string().describe("Suchbegriff oder Thema, z.B. 'three act structure', 'character arc', 'adaptation techniques', 'sequence approach'"),
    max_results: z.number().optional().default(5).describe("Maximale Anzahl Treffer (1-10)"),
  },
  async ({ query, max_results }) => {
    const results = searchChunks(query, "theory", Math.min(max_results, 10));
    return { content: [{ type: "text", text: formatResults(results) }] };
  }
);

// Tool: search_screenplays
server.tool(
  "search_screenplays",
  "Durchsucht professionelle Drehbücher nach einem Stichwort, einer Technik oder einem Motiv. Enthält u.a. Atonement, Doctor Zhivago, Grand Budapest Hotel, The Godfather, und viele mehr. Besonders nützlich um zu sehen, wie professionelle Autoren bestimmte Szenen, Dialoge oder Techniken umsetzen.",
  {
    query: z.string().describe("Suchbegriff, z.B. 'snowstorm', 'love confession', 'inner monologue', 'montage sequence'"),
    only_adaptations: z.boolean().optional().default(false).describe("Nur Drehbücher zeigen, die auf Romanen basieren"),
    max_results: z.number().optional().default(5).describe("Maximale Anzahl Treffer (1-10)"),
  },
  async ({ query, only_adaptations, max_results }) => {
    let results = searchChunks(query, "screenplay", Math.min(max_results, 10));
    if (only_adaptations) {
      results = results.filter((r) => r.doc.is_adaptation);
    }
    return { content: [{ type: "text", text: formatResults(results) }] };
  }
);

// Tool: search_treatments
server.tool(
  "search_treatments",
  "Durchsucht professionelle Film-Treatments nach einem Stichwort. Enthält Treatments von Star Wars, E.T., Spider-Man, Batman, X-Men, Strange Days u.a. Nützlich um Treatment-Format und -Stil zu studieren.",
  {
    query: z.string().describe("Suchbegriff, z.B. 'opening scene', 'climax', 'character introduction'"),
    max_results: z.number().optional().default(5).describe("Maximale Anzahl Treffer (1-10)"),
  },
  async ({ query, max_results }) => {
    const results = searchChunks(query, "treatment", Math.min(max_results, 10));
    return { content: [{ type: "text", text: formatResults(results) }] };
  }
);

// Tool: search_all
server.tool(
  "search_all",
  "Durchsucht den gesamten Referenz-Korpus (Theorie + Screenplays + Treatments) nach einem Begriff.",
  {
    query: z.string().describe("Suchbegriff"),
    max_results: z.number().optional().default(5).describe("Maximale Anzahl Treffer (1-10)"),
  },
  async ({ query, max_results }) => {
    const results = searchChunks(query, null, Math.min(max_results, 10));
    return { content: [{ type: "text", text: formatResults(results) }] };
  }
);

// Tool: get_document_excerpt
server.tool(
  "get_document_excerpt",
  "Liest einen bestimmten Abschnitt eines Dokuments. Nützlich wenn du mehr Kontext aus einer bestimmten Quelle brauchst.",
  {
    title: z.string().describe("Titel oder Teil des Titels des Dokuments"),
    chunk_start: z.number().optional().default(0).describe("Start-Chunk (0-basiert)"),
    chunk_count: z.number().optional().default(3).describe("Anzahl Chunks zu lesen (1-5)"),
  },
  async ({ title, chunk_start, chunk_count }) => {
    const titleLower = title.toLowerCase();
    const doc = index.documents.find((d) => d.title.toLowerCase().includes(titleLower));

    if (!doc) {
      return {
        content: [{ type: "text", text: `Dokument "${title}" nicht gefunden. Nutze list_references für verfügbare Dokumente.` }],
      };
    }

    const docChunks = index.chunks
      .filter((c) => c.doc_id === doc.id)
      .slice(chunk_start, chunk_start + Math.min(chunk_count, 5));

    const text = docChunks.map((c) => c.text).join("\n\n---\n\n");

    return {
      content: [{
        type: "text",
        text: `Quelle: ${doc.title} [${doc.category}]\nChunks ${chunk_start + 1}-${chunk_start + docChunks.length} von ${doc.chunk_count}\n\n${text}`,
      }],
    };
  }
);

// Tool: list_references
server.tool(
  "list_references",
  "Zeigt alle verfügbaren Referenzdokumente, gruppiert nach Kategorie.",
  {
    category: z.enum(["all", "theory", "screenplay", "treatment"]).optional().default("all").describe("Kategorie filtern"),
  },
  async ({ category }) => {
    let docs = index.documents;
    if (category !== "all") {
      docs = docs.filter((d) => d.category === category);
    }

    const grouped = {};
    for (const doc of docs) {
      if (!grouped[doc.category]) grouped[doc.category] = [];
      grouped[doc.category].push(doc);
    }

    let text = `Referenzmaterial: ${docs.length} Dokumente\n\n`;

    for (const [cat, catDocs] of Object.entries(grouped)) {
      text += `\n═══ ${cat.toUpperCase()} (${catDocs.length}) ═══\n`;
      for (const doc of catDocs) {
        const adapted = doc.is_adaptation ? " [ADAPTION]" : "";
        text += `  • ${doc.title}${adapted} — ${doc.chunk_count} Chunks\n`;
      }
    }

    return { content: [{ type: "text", text }] };
  }
);

// ── Server starten ───────────────────────────────────────────

const transport = new StdioServerTransport();
await server.connect(transport);
