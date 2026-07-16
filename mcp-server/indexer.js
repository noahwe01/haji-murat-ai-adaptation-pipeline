/**
 * INDEXER — Baut Suchindex aus den vorab extrahierten Textdateien.
 * Nutzung: node indexer.js
 */

import fs from "fs";
import path from "path";

const EXTRACTED_DIR = path.resolve("./extracted");
const INDEX_FILE = path.resolve("./index.json");

const CHUNK_SIZE = 2000;
const CHUNK_OVERLAP = 300;
const MIN_TEXT_LENGTH = 500;

// ── Kategorisierung ─────────────────────────────────────────

function categorize(filename) {
  const theoryPatterns = [
    "Robert McKee", "Robert Mckee", "Syd Field", "Linda Seger", "Art of dramatic writing",
    "Art of Adaptation", "Tools of Screenwriting", "Tools+of+Screenwriting",
    "8 Sequence", "Was ist ein Filmtreatment", "preview-978",
    "Blake Snyder", "Gloria Kempton",
  ];
  const treatmentPatterns = ["Treatment", "treatment"];

  if (theoryPatterns.some((p) => filename.includes(p))) return "theory";
  if (treatmentPatterns.some((p) => filename.includes(p))) return "treatment";
  return "screenplay";
}

function extractTitle(filename) {
  return filename
    .replace(/\.txt$|\.htm$/i, "")
    .replace(/[_+]/g, " ")
    .replace(/-/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const ADAPTATIONS = new Set([
  "atonement", "doctor zhivago 1965", "Forrest Gump", "Schindler list",
  "THE AGE OF INNOCENCE", "The Pianist", "callmebyyourname screenplay",
  "no country for old men", "The Silence of the Lambs", "The Exorcist",
  "TheGreenMile", "L.A. Confidential", "The French Connection", "goodfellas",
  "the godfather 1972", "Dances With Wolves", "12YAS SCRIPT BK COVER PAGES FINAL",
  "jojo rabbit final script", "arrival", "Brief Encounter",
  "Letter from an Unknown Woman", "Bright Star", "Cold War",
]);

function isAdaptation(title) {
  return ADAPTATIONS.has(title);
}

// ── Chunking ─────────────────────────────────────────────────

function chunkText(text) {
  const chunks = [];
  const step = CHUNK_SIZE - CHUNK_OVERLAP;
  let start = 0;

  while (start < text.length) {
    const end = Math.min(start + CHUNK_SIZE, text.length);
    const chunk = text.substring(start, end).trim();
    if (chunk.length > 50) {
      chunks.push(chunk);
    }
    start += step;
  }

  return chunks;
}

// ── Hauptprogramm ────────────────────────────────────────────

const files = fs.readdirSync(EXTRACTED_DIR).filter((f) => {
  const ext = path.extname(f).toLowerCase();
  return [".txt", ".htm"].includes(ext);
});

console.log(`${"═".repeat(60)}`);
console.log(`  INDEXER — ${files.length} Dateien verarbeiten`);
console.log(`${"═".repeat(60)}\n`);

const documents = [];
const chunks = [];

for (const file of files) {
  const filepath = path.join(EXTRACTED_DIR, file);
  const text = fs.readFileSync(filepath, "utf-8");

  if (text.length < MIN_TEXT_LENGTH) {
    console.log(`  ⚠ Übersprungen (${text.length} bytes): ${file}`);
    continue;
  }

  const category = categorize(file);
  const title = extractTitle(file);
  const adapted = isAdaptation(title);
  const fileChunks = chunkText(text);
  const docId = documents.length;

  documents.push({
    id: docId,
    filename: file,
    title,
    category,
    is_adaptation: adapted,
    text_length: text.length,
    chunk_count: fileChunks.length,
  });

  for (let i = 0; i < fileChunks.length; i++) {
    chunks.push({
      doc_id: docId,
      chunk_index: i,
      total_chunks: fileChunks.length,
      text: fileChunks[i],
    });
  }

  console.log(
    `  [${category.padEnd(10)}] ${title.substring(0, 45).padEnd(47)} ` +
    `${fileChunks.length.toString().padStart(4)} Chunks  ${(text.length / 1000).toFixed(0).padStart(4)}k`
  );
}

const index = {
  meta: {
    created: new Date().toISOString(),
    files_total: documents.length,
    chunks_total: chunks.length,
    categories: {
      theory: documents.filter((d) => d.category === "theory").length,
      treatment: documents.filter((d) => d.category === "treatment").length,
      screenplay: documents.filter((d) => d.category === "screenplay").length,
    },
  },
  documents,
  chunks,
};

fs.writeFileSync(INDEX_FILE, JSON.stringify(index), "utf-8");
const sizeMB = (fs.statSync(INDEX_FILE).size / 1024 / 1024).toFixed(1);

console.log(`\n${"═".repeat(60)}`);
console.log(`  INDEX ERSTELLT`);
console.log(`  Dokumente:  ${documents.length}`);
console.log(`  Chunks:     ${chunks.length}`);
console.log(`  Theorie:    ${index.meta.categories.theory}`);
console.log(`  Treatments: ${index.meta.categories.treatment}`);
console.log(`  Screenplays:${index.meta.categories.screenplay}`);
console.log(`  Größe:      ${sizeMB} MB`);
console.log(`${"═".repeat(60)}`);
