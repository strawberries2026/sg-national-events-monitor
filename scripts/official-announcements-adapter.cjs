'use strict';
// Read-only bridge from existing public announcements to Phase 2 news cards.
// No network requests, scraping or modifications to verified event data.
const { normalize, deduplicate } = require('./news-normalizer.cjs');
const OFFICIAL_AGENCIES = new Set(['PMO','ISTANA','MFA','MHA','MOF','MINDEF','PARLIAMENT']);
function fromOfficialAnnouncements(payload) {
  if (!payload || !Array.isArray(payload.events)) return [];
  const converted = payload.events
    .filter(x => x && x.type === 'Published announcement' && typeof x.agency === 'string')
    .map(x => {
      const agency = x.agency.trim().toUpperCase();
      if (!OFFICIAL_AGENCIES.has(agency)) return null;
      const result = normalize({
        title: x.title, url: x.source_url,
        published_at: typeof x.published_date === 'string' ? x.published_date + 'T00:00:00+08:00' : null,
        categories: [x.category || 'Announcements']
      }, { id: agency.toLowerCase(), name: agency, kind: 'official' });
      if (result) {
        result.verification_status = 'official_source_reported';
        result.event_start = null;
        result.event_end = null;
      }
      return result;
    });
  return deduplicate(converted);
}
module.exports = { fromOfficialAnnouncements };
