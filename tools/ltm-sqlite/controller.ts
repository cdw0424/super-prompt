// Dev-only reference controller (not published)
import Ajv from 'ajv';
import Database from 'better-sqlite3';
import Redis from 'ioredis';

const ajv = new Ajv({ allErrors: true, useDefaults: true });
// eslint-disable-next-line @typescript-eslint/no-var-requires
const validateMemory = ajv.compile(require('./schemas/memory.fact.json'));

const db = new Database('./ltm.db');
db.pragma('journal_mode = WAL');
db.pragma('synchronous = NORMAL');

const redis = new Redis(process.env.REDIS_URL || '');

export async function createMemory(payload: any, embedding?: Float32Array) {
  if (!validateMemory(payload)) {
    throw new Error('VALIDATION_ERROR:' + JSON.stringify(validateMemory.errors));
  }
  const tx = db.transaction(() => {
    const ins = db.prepare(`
      INSERT INTO memory(project_id, kind, source, author, title, body, tags, importance, pinned, tokens, expires_at)
      VALUES (@project_id, @kind, @source, @author, @title, @body, @tags, @importance, @pinned, 0, @expires_at)
    `);
    const { lastInsertRowid: id } = ins.run(payload);

    if (embedding) {
      const buf = Buffer.from(new Float32Array(embedding).buffer);
      db.prepare(`
        INSERT INTO embedding(memory_id, dim, vector)
        VALUES (?, ?, ?)
        ON CONFLICT(memory_id) DO UPDATE SET dim=excluded.dim, vector=excluded.vector
      `).run(Number(id), embedding.length, buf);
    }
    return id;
  });
  const id = tx();
  await redis.del(`memory:project:${payload.project_id}:search:*`);
  return id;
}

export function searchHybrid({ projectId, queryText, queryVec, k = 8 }: any) {
  const candidatesN = Math.max(150, k * 20);
  const ftsRows = db.prepare(`
    WITH f AS (
      SELECT m.id, (1.0 / (1.0 + bm25(memory_fts))) AS bm25_norm, m.importance, m.pinned
      FROM memory_fts
      JOIN memory m ON m.id = memory_fts.rowid
      WHERE m.project_id = ? 
        AND (m.expires_at IS NULL OR m.expires_at > datetime('now'))
        AND memory_fts MATCH ?
      ORDER BY bm25(memory_fts) ASC
      LIMIT ?
    )
    SELECT * FROM f
  `).all(projectId, queryText, candidatesN);

  if (!queryVec) return loadByIds(ftsRows.slice(0, k).map((r: any) => r.id));

  const ids = ftsRows.map((r: any) => r.id);
  if (!ids.length) return [];
  const emb = db.prepare(
    `SELECT memory_id, dim, vector FROM embedding WHERE memory_id IN (${ids.map(() => '?').join(',')})`
  ).all(...ids);

  const vecMap = new Map<number, Float32Array>();
  for (const r of emb as any[]) {
    const v = new Float32Array((r as any).vector.buffer, (r as any).vector.byteOffset, (r as any).vector.byteLength / 4);
    vecMap.set(r.memory_id, v);
  }

  const rescored = ftsRows
    .map((r: any) => {
      const v = vecMap.get(r.id);
      const cosine = v ? cosineSim(queryVec, v) : 0;
      const score = 0.6 * cosine + 0.3 * r.bm25_norm + 0.1 * r.importance + (r.pinned ? 0.05 : 0);
      return { id: r.id, score };
    })
    .sort((a: any, b: any) => b.score - a.score)
    .slice(0, k);

  return loadByIds(rescored.map((r: any) => r.id));
}

function loadByIds(ids: number[]) {
  const rows = db
    .prepare(
      `SELECT id, kind, title, body, tags, importance, pinned, created_at
       FROM memory WHERE id IN (${ids.map(() => '?').join(',')})`
    )
    .all(...ids);
  const idx = new Map(ids.map((id, i) => [id, i] as const));
  return rows.sort((a: any, b: any) => (idx.get(a.id) as number) - (idx.get(b.id) as number));
}

function cosineSim(a: Float32Array, b: Float32Array) {
  let dot = 0,
    na = 0,
    nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb) + 1e-12);
}

