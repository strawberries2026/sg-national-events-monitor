'use strict';
// Phase 2: pure functions only; no network calls or private data.
const httpsUrl = value => {
  try { const u = new URL(String(value)); return u.protocol === 'https:' ? u.href : null; }
  catch { return null; }
};
const validDate = value => {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
  const d = new Date(value + 'T00:00:00Z');
  return Number.isFinite(d.valueOf()) && d.toISOString().slice(0,10) === value ? value : null;
};
const normalize = (raw, source) => {
  if (!raw || !source || !['official','news','social'].includes(source.kind)) return null;
  const url = httpsUrl(raw.url || raw.link);
  const title = String(raw.title || '').trim().replace(/\s+/g,' ').slice(0,300);
  if (!url || !title) return null;
  const timestamp = Date.parse(raw.published_at || raw.pubDate || '');
  const published_at = Number.isFinite(timestamp) ? new Date(timestamp).toISOString() : null;
  const event_start = validDate(raw.event_start);
  const event_end = validDate(raw.event_end);
  return {
    id: source.id + ':' + url,
    title, canonical_url:url, publisher:source.name, source_class:source.kind,
    published_at, event_start, event_end:event_start ? (event_end || event_start) : null,
    persons:Array.isArray(raw.persons) ? raw.persons.filter(x=>typeof x==='string').slice(0,12) : [],
    categories:Array.isArray(raw.categories) ? raw.categories.filter(x=>typeof x==='string').slice(0,12) : [],
    verification_status:'reported',
    verification_url:null
  };
};
const deduplicate = records => {
  const seen = new Set();
  return records.filter(record => {
    if (!record) return false;
    const key = record.canonical_url.toLowerCase().replace(/\/$/,'');
    if (seen.has(key)) return false;
    seen.add(key); return true;
  });
};
module.exports = {httpsUrl, validDate, normalize, deduplicate};
