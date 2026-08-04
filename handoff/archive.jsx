// Direction A — Archive.
// Scholarly, library-coded, calm. Warm cream paper, deep ink, oxblood accent.
// EB Garamond display + JetBrains Mono labels + Source Sans 3 body.
// Bold idea: recent dissertations rendered as spines on the "shelf".

// Palette is exposed via CSS custom properties on <html> so it can be
// swapped at runtime (see archive.html's palette switcher). Defaults live
// there; these constants are just thin wrappers so every component reads
// the same names.
const A_PAPER  = 'var(--paper)';
const A_PAPER2 = 'var(--paper2)';
const A_PAPER3 = 'var(--paper3)';
const A_INK    = 'var(--ink)';
const A_INK2   = 'var(--ink2)';
const A_MUTE   = 'var(--mute)';
const A_LINE   = 'var(--line)';
const A_LINE2  = 'var(--line2)';
const A_OX     = 'var(--accent)';
const A_AVATAR = 'var(--avatar)';

const aRoot = {
  fontFamily: '"Source Sans 3", -apple-system, sans-serif',
  color: A_INK,
  background: A_PAPER,
  width: '100%',
  height: '100%',
  overflow: 'hidden',
  fontSize: 15,
  lineHeight: 1.55,
  letterSpacing: 0,
};

const aSerif = { fontFamily: '"EB Garamond", "Source Serif 4", Georgia, serif' };
const aMono = { fontFamily: '"JetBrains Mono", ui-monospace, Menlo, monospace' };
const aCaps = { ...aMono, textTransform: 'uppercase', letterSpacing: '0.14em', fontSize: 11, fontWeight: 500 };
const aRule = { borderBottom: `1px solid ${A_LINE}` };
const aRuleSoft = { borderBottom: `1px solid ${A_LINE2}` };

function ANav({ active }) {
  const link = (id, label) => (
    <a key={id} href="#" style={{
      ...aCaps,
      color: id === active ? A_OX : A_INK2,
      textDecoration: 'none',
      paddingBottom: 4,
      borderBottom: id === active ? `2px solid ${A_OX}` : '2px solid transparent',
    }}>{label}</a>
  );
  return (
    <header style={{ padding: '28px 64px 24px', borderBottom: `1px solid ${A_LINE}`, background: A_PAPER }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 18 }}>
        <a href="#" style={{ textDecoration: 'none', color: A_INK }}>
          <div style={{ ...aCaps, color: A_MUTE, marginBottom: 2 }}>Est. 2024 · Vol. I</div>
          <div style={{ ...aSerif, fontSize: 32, fontWeight: 500, lineHeight: 1, letterSpacing: -0.4 }}>
            The History Dissertation Database
          </div>
        </a>
        <div style={{ ...aMono, fontSize: 12, color: A_MUTE, textAlign: 'right', lineHeight: 1.4 }}>
          12,418 dissertations<br/>4,932 scholars · 1,206 advisors
        </div>
      </div>
      <nav style={{ display: 'flex', gap: 36, alignItems: 'center' }}>
        {link('diss', 'Dissertations')}
        {link('scholars', 'Scholars')}
        {link('committee', 'Committee Members')}
        {link('about', 'About')}
        {link('contribute', 'Contribute')}
        <div style={{ flex: 1 }} />
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, border: `1px solid ${A_LINE}`, padding: '6px 12px', background: A_PAPER3 }}>
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke={A_MUTE} strokeWidth="1.5"><circle cx="7" cy="7" r="5"/><path d="M11 11l3.5 3.5"/></svg>
          <input placeholder="Search titles, scholars, advisors…" style={{ border: 'none', outline: 'none', background: 'transparent', fontFamily: 'inherit', fontSize: 13, color: A_INK2, width: 320 }} />
        </div>
      </nav>
    </header>
  );
}

function AFooter() {
  return (
    <footer style={{ padding: '40px 64px 56px', borderTop: `1px solid ${A_LINE}`, marginTop: 64, background: A_PAPER2 }}>
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: 48, alignItems: 'flex-start' }}>
        <div>
          <div style={{ ...aSerif, fontSize: 22, fontWeight: 500, marginBottom: 8 }}>The History Dissertation Database</div>
          <div style={{ fontSize: 13, color: A_INK2, maxWidth: 380 }}>
            A working catalogue of doctoral dissertations in history. Data contributed by departments and the American Historical Association.
          </div>
        </div>
        {[
          ['Explore', ['Dissertations', 'Scholars', 'Committee Members', 'Institutions', 'Decades']],
          ['About', ['Project', 'Contributing', 'Method', 'Changelog']],
          ['Hosted at', ['RRCHNM', 'George Mason University']],
        ].map(([h, items]) => (
          <div key={h}>
            <div style={{ ...aCaps, color: A_MUTE, marginBottom: 10 }}>{h}</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: 13, color: A_INK2 }}>
              {items.map(t => <a key={t} href="#" style={{ color: 'inherit', textDecoration: 'none' }}>{t}</a>)}
            </div>
          </div>
        ))}
      </div>
    </footer>
  );
}

function AHome() {
  const featured = DISSERTATIONS[1];
  const decades = [
    { label: '1980s', count: 612 }, { label: '1990s', count: 1184 },
    { label: '2000s', count: 2247 }, { label: '2010s', count: 4108 }, { label: '2020s', count: 1893 },
  ];
  return (
    <div style={aRoot}>
      <ANav active="home" />

      {/* Hero — quiet, two-column */}
      <section style={{ padding: '72px 64px 56px', display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 80, alignItems: 'flex-start' }}>
        <div>
          <div style={{ ...aCaps, color: A_OX, marginBottom: 18 }}>An open scholarly index</div>
          <h1 style={{ ...aSerif, fontWeight: 500, fontSize: 60, lineHeight: 1.05, letterSpacing: -1.2, margin: '0 0 28px' }}>
            A catalogue of <em style={{ color: A_OX }}>history</em><br/>
            and the scholars who<br/>
            shaped its writing.
          </h1>
          <p style={{ fontSize: 18, lineHeight: 1.6, color: A_INK2, maxWidth: 540, margin: 0 }}>
            Browse fifty years of doctoral work — dissertations, their authors, advisors, and the committee members who quietly steer the discipline. Built for historiographers and researchers.
          </p>
          <div style={{ display: 'flex', gap: 12, marginTop: 32 }}>
            <a href="#" style={{ padding: '12px 22px', background: A_INK, color: A_PAPER, textDecoration: 'none', ...aCaps, color: A_PAPER }}>Browse the catalogue</a>
            <a href="#" style={{ padding: '12px 22px', border: `1px solid ${A_INK}`, color: A_INK, textDecoration: 'none', ...aCaps, color: A_INK }}>Search a scholar</a>
          </div>
        </div>

        {/* Featured plate */}
        <aside style={{ border: `1px solid ${A_LINE}`, background: A_PAPER3, padding: 28, position: 'relative' }}>
          <div style={{ ...aCaps, color: A_OX, marginBottom: 14 }}>Featured this month</div>
          <div style={{ ...aMono, fontSize: 11, color: A_MUTE, marginBottom: 6 }}>{featured.id} · {featured.year}</div>
          <div style={{ ...aSerif, fontSize: 26, lineHeight: 1.2, fontWeight: 500, marginBottom: 14 }}>{featured.title}</div>
          <div style={{ fontSize: 14, color: A_INK2, marginBottom: 22 }}>
            <span style={aSerif}><em>by</em></span> {featured.author}<br/>
            <span style={aSerif}><em>at</em></span> {featured.institution}<br/>
            <span style={aSerif}><em>under</em></span> {featured.advisor}
          </div>
          <div style={{ ...aRuleSoft, paddingBottom: 14, marginBottom: 14 }} />
          <div style={{ ...aCaps, color: A_MUTE, marginBottom: 8 }}>Abstract — opening</div>
          <p style={{ fontSize: 14, lineHeight: 1.6, color: A_INK2, margin: 0, fontStyle: 'italic', ...aSerif }}>
            “The salted page argues that print and labor were not separate orders in the Atlantic of 1700, but a single moving archive — wet, scarce, transcribed by hands more familiar with rigging than with rules…”
          </p>
          <a href="#" style={{ display: 'inline-block', marginTop: 18, color: A_OX, textDecoration: 'none', ...aCaps }}>Read full entry →</a>
        </aside>
      </section>

      {/* Editorial mid-section: recently catalogued + at-a-glance sidebar.
          Two-column rhythm matches the hero above; the column rule (Source
          Serif sized for a comfortable read) acts as the headline of an
          editorial spread. */}
      <section style={{ padding: '8px 64px 56px', display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 64 }}>
        {/* Recently catalogued */}
        <div>
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 18, paddingBottom: 12, borderBottom: `2px solid ${A_INK}` }}>
            <h2 style={{ ...aSerif, fontSize: 30, margin: 0, fontWeight: 500, letterSpacing: -0.4 }}>Recently catalogued</h2>
            <a href="#" style={{ ...aCaps, color: A_OX, textDecoration: 'none' }}>See all 142 →</a>
          </div>
          {DISSERTATIONS.slice(0, 6).map(d => (
            <a key={d.id} href="#" style={{ display: 'grid', gridTemplateColumns: '64px 1fr 170px', gap: 24, padding: '22px 0', borderBottom: `1px solid ${A_LINE2}`, textDecoration: 'none', color: A_INK, alignItems: 'flex-start' }}>
              <div style={{ ...aMono, fontSize: 13, color: A_OX, fontWeight: 600, paddingTop: 5 }}>{d.year}</div>
              <div>
                <div style={{ ...aSerif, fontSize: 22, fontWeight: 500, lineHeight: 1.25, letterSpacing: -0.2, marginBottom: 5 }}>{d.title}</div>
                <div style={{ fontSize: 14, color: A_INK2 }}>
                  <span style={{ ...aSerif, fontStyle: 'italic' }}>by</span>{' '}
                  <span style={{ color: A_OX }}>{d.author}</span>
                  <span style={{ color: A_MUTE, margin: '0 8px' }}>·</span>{d.institution}
                </div>
              </div>
              <div style={{ paddingTop: 4, textAlign: 'right' }}>
                <div style={{ ...aCaps, color: A_MUTE, marginBottom: 4 }}>Advised by</div>
                <div style={{ fontSize: 14, ...aSerif, fontStyle: 'italic' }}>{d.advisor}</div>
              </div>
            </a>
          ))}
        </div>

        {/* Sidebar — numbers, advisors, field note */}
        <aside>
          <div style={{ marginBottom: 36 }}>
            <div style={{ ...aCaps, color: A_MUTE, marginBottom: 12, paddingBottom: 8, borderBottom: `2px solid ${A_INK}` }}>By the numbers</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0 }}>
              {[['12,418', 'dissertations'], ['4,932', 'scholars'], ['1,206', 'advisors'], ['218', 'institutions'], ['1965', 'first record'], ['2024', 'most recent']].map(([v, k]) => (
                <div key={k} style={{ padding: '14px 0', borderBottom: `1px solid ${A_LINE2}` }}>
                  <div style={{ ...aSerif, fontSize: 30, fontWeight: 500, color: A_INK, letterSpacing: -0.4, lineHeight: 1 }}>{v}</div>
                  <div style={{ ...aCaps, color: A_MUTE, marginTop: 4 }}>{k}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 36 }}>
            <div style={{ ...aCaps, color: A_MUTE, marginBottom: 12, paddingBottom: 8, borderBottom: `2px solid ${A_INK}` }}>Heavy advisors · last decade</div>
            {COMMITTEE.slice(0, 5).map((c, i) => (
              <a key={c.name} href="#" style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', padding: '12px 0', borderBottom: `1px solid ${A_LINE2}`, textDecoration: 'none', color: A_INK }}>
                <span>
                  <span style={{ ...aMono, fontSize: 11, color: A_MUTE, marginRight: 10 }}>{String(i + 1).padStart(2, '0')}</span>
                  <span style={{ ...aSerif, fontSize: 18, fontWeight: 500 }}>{c.name}</span>
                </span>
                <span style={{ ...aMono, fontSize: 12, color: A_OX }}>{c.advised}</span>
              </a>
            ))}
          </div>

          <div style={{ background: A_PAPER2, padding: 22, border: `1px solid ${A_LINE}` }}>
            <div style={{ ...aCaps, color: A_OX, marginBottom: 10 }}>Field note</div>
            <div style={{ ...aSerif, fontSize: 19, lineHeight: 1.4, marginBottom: 12, fontWeight: 500 }}>
              Spotted a missing committee member or a wrong year? <span style={{ color: A_OX }}>Submit a correction.</span>
            </div>
            <a href="#" style={{ ...aCaps, color: A_INK, textDecoration: 'underline', textUnderlineOffset: 4 }}>Contributor guide →</a>
          </div>
        </aside>
      </section>

      {/* Browse rails */}
      <section style={{ padding: '0 64px 24px', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 48 }}>
        <div>
          <div style={{ ...aCaps, color: A_MUTE, marginBottom: 14 }}>Browse by decade</div>
          {decades.map(d => (
            <a key={d.label} href="#" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '10px 0', borderBottom: `1px solid ${A_LINE2}`, textDecoration: 'none', color: A_INK }}>
              <span style={{ ...aSerif, fontSize: 22 }}>{d.label}</span>
              <span style={{ ...aMono, fontSize: 12, color: A_MUTE }}>{d.count.toLocaleString()}</span>
            </a>
          ))}
        </div>
        <div>
          <div style={{ ...aCaps, color: A_MUTE, marginBottom: 14 }}>Browse by field</div>
          {['American', 'European', 'East Asia', 'South Asia', 'Latin America', 'Africa', 'Middle East', 'Atlantic'].map(f => (
            <a key={f} href="#" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '7px 0', borderBottom: `1px solid ${A_LINE2}`, textDecoration: 'none', color: A_INK }}>
              <span style={{ ...aSerif, fontSize: 17 }}>{f} history</span>
              <span style={{ ...aMono, fontSize: 11, color: A_MUTE }}>—</span>
            </a>
          ))}
        </div>
        <div style={{ background: A_PAPER2, padding: 24, border: `1px solid ${A_LINE}` }}>
          <div style={{ ...aCaps, color: A_OX, marginBottom: 14 }}>Contribute</div>
          <div style={{ ...aSerif, fontSize: 22, lineHeight: 1.3, marginBottom: 12 }}>
            Did your committee miss a record? Help us fill the gaps.
          </div>
          <p style={{ fontSize: 14, color: A_INK2, margin: '0 0 18px' }}>
            Add dissertations, correct an advisor, or submit a new scholar. Edits are reviewed by the editorial team.
          </p>
          <a href="#" style={{ ...aCaps, color: A_INK, textDecoration: 'underline', textUnderlineOffset: 4 }}>Read the guide →</a>
        </div>
      </section>

      <AFooter />
    </div>
  );
}

// ── Table primitives ──────────────────────────────────────────
function ATableHeader({ title, count, subtitle }) {
  return (
    <section style={{ padding: '56px 64px 28px', borderBottom: `1px solid ${A_LINE}` }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div>
          <div style={{ ...aCaps, color: A_OX, marginBottom: 10 }}>{subtitle}</div>
          <h1 style={{ ...aSerif, fontSize: 48, margin: 0, fontWeight: 500, letterSpacing: -0.6 }}>{title}</h1>
        </div>
        <div style={{ ...aMono, fontSize: 12, color: A_MUTE, textAlign: 'right' }}>
          showing <span style={{ color: A_INK }}>1–18</span> of <span style={{ color: A_INK }}>{count}</span>
        </div>
      </div>
    </section>
  );
}

function AFilterBar({ filters }) {
  return (
    <div style={{ padding: '20px 64px', borderBottom: `1px solid ${A_LINE}`, background: A_PAPER2, display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
      <span style={{ ...aCaps, color: A_MUTE }}>Filter</span>
      {filters.map(f => (
        <button key={f.label} style={{
          ...aMono, fontSize: 12, padding: '6px 12px',
          background: f.active ? A_INK : 'transparent',
          color: f.active ? A_PAPER : A_INK2,
          border: f.active ? `1px solid ${A_INK}` : `1px solid ${A_LINE}`,
          cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
        }}>
          {f.label}
          <span style={{ opacity: 0.5 }}>▾</span>
        </button>
      ))}
      <div style={{ flex: 1 }} />
      <span style={{ ...aCaps, color: A_MUTE }}>Sort</span>
      <button style={{ ...aMono, fontSize: 12, padding: '6px 12px', background: 'transparent', border: `1px solid ${A_LINE}`, cursor: 'pointer' }}>
        Year ↓
      </button>
    </div>
  );
}

function APagination() {
  return (
    <div style={{ padding: '32px 64px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
      {['‹', '1', '2', '3', '4', '5', '…', '687', '›'].map((p, i) => (
        <button key={i} style={{
          ...aMono, fontSize: 13, padding: '8px 14px', minWidth: 36,
          background: p === '2' ? A_INK : 'transparent',
          color: p === '2' ? A_PAPER : A_INK2,
          border: `1px solid ${p === '2' ? A_INK : A_LINE}`,
          cursor: 'pointer',
        }}>{p}</button>
      ))}
    </div>
  );
}

function ADissTable() {
  return (
    <div style={aRoot}>
      <ANav active="diss" />
      <ATableHeader subtitle="Catalogue · primary index" title="Dissertations" count="12,418" />
      <AFilterBar filters={[
        { label: 'Year: 2015–2024', active: true },
        { label: 'Field: any' },
        { label: 'Institution: any' },
        { label: 'Advisor: any' },
        { label: 'Region: any' },
      ]} />

      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
        <thead>
          <tr style={{ borderBottom: `2px solid ${A_INK}` }}>
            {['Year', 'Title & Author', 'Institution', 'Advisor', 'Field'].map((h, i) => (
              <th key={h} style={{ ...aCaps, color: A_MUTE, padding: '14px 24px', textAlign: i === 0 ? 'left' : 'left', fontWeight: 500 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {DISSERTATIONS.map((d, i) => (
            <tr key={d.id} style={{ borderBottom: `1px solid ${A_LINE2}`, background: i % 2 ? 'transparent' : 'rgba(255,255,255,0.4)' }}>
              <td style={{ padding: '18px 24px', verticalAlign: 'top', ...aMono, fontSize: 13, color: A_INK2, width: 80 }}>{d.year}</td>
              <td style={{ padding: '18px 24px', verticalAlign: 'top' }}>
                <div style={{ ...aSerif, fontSize: 18, lineHeight: 1.3, marginBottom: 4, fontWeight: 500 }}>
                  <a href="#" style={{ color: A_INK, textDecoration: 'none' }}>{d.title}</a>
                </div>
                <div style={{ fontSize: 13, color: A_INK2 }}>
                  <span style={{ ...aSerif, fontStyle: 'italic' }}>by</span> <a href="#" style={{ color: A_OX, textDecoration: 'none' }}>{d.author}</a>
                  <span style={{ color: A_MUTE, margin: '0 8px' }}>·</span>
                  <span style={{ ...aMono, fontSize: 11, color: A_MUTE }}>{d.id}</span>
                </div>
              </td>
              <td style={{ padding: '18px 24px', verticalAlign: 'top', fontSize: 13, color: A_INK2, maxWidth: 180 }}>{d.institution}</td>
              <td style={{ padding: '18px 24px', verticalAlign: 'top', fontSize: 13 }}>
                <a href="#" style={{ color: A_INK, textDecoration: 'none', borderBottom: `1px dotted ${A_MUTE}` }}>{d.advisor}</a>
              </td>
              <td style={{ padding: '18px 24px', verticalAlign: 'top' }}>
                <span style={{ ...aMono, fontSize: 11, color: A_INK2, border: `1px solid ${A_LINE}`, padding: '2px 8px', background: A_PAPER3 }}>{d.subject}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <APagination />
    </div>
  );
}

function AScholars() {
  const rows = SCHOLARS.slice(0, 12);
  return (
    <div style={aRoot}>
      <ANav active="scholars" />
      <ATableHeader subtitle="People · authors of dissertations" title="Scholars" count="4,932" />
      <AFilterBar filters={[
        { label: 'Status: any', active: true },
        { label: 'Institution: any' },
        { label: 'Field: any' },
        { label: 'Cohort: any' },
      ]} />

      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
        <thead>
          <tr style={{ borderBottom: `2px solid ${A_INK}` }}>
            {['Scholar', 'Institution', 'Position', 'Fields', 'Advised', 'Committee'].map(h => (
              <th key={h} style={{ ...aCaps, color: A_MUTE, padding: '14px 24px', textAlign: 'left', fontWeight: 500 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((s, i) => (
            <tr key={s.name} style={{ borderBottom: `1px solid ${A_LINE2}`, background: i % 2 ? 'transparent' : 'rgba(255,255,255,0.4)' }}>
              <td style={{ padding: '14px 24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                  <div style={{ width: 36, height: 36, borderRadius: 18, background: A_AVATAR, border: `1px solid ${A_LINE}`, display: 'flex', alignItems: 'center', justifyContent: 'center', ...aSerif, fontSize: 14, color: A_OX, fontStyle: 'italic' }}>
                    {s.name.split(' ').map(p => p[0]).slice(0, 2).join('')}
                  </div>
                  <a href="#" style={{ ...aSerif, fontSize: 18, fontWeight: 500, color: A_INK, textDecoration: 'none' }}>{s.name}</a>
                </div>
              </td>
              <td style={{ padding: '14px 24px', fontSize: 13, color: A_INK2 }}>{s.institution}</td>
              <td style={{ padding: '14px 24px', fontSize: 13, color: A_INK2, ...aSerif, fontStyle: 'italic' }}>{s.role}</td>
              <td style={{ padding: '14px 24px' }}>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {s.fields.map(f => (
                    <span key={f} style={{ ...aMono, fontSize: 11, color: A_INK2, border: `1px solid ${A_LINE}`, padding: '2px 8px', background: A_PAPER3 }}>{f}</span>
                  ))}
                </div>
              </td>
              <td style={{ padding: '14px 24px', ...aMono, fontSize: 13, color: A_INK }}>{s.advised || '—'}</td>
              <td style={{ padding: '14px 24px', ...aMono, fontSize: 13, color: A_INK }}>{s.committee || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <APagination />
    </div>
  );
}

function ACommittee() {
  return (
    <div style={aRoot}>
      <ANav active="committee" />
      <ATableHeader subtitle="People · advisors and readers" title="Committee Members" count="1,206" />
      <AFilterBar filters={[
        { label: 'Institution: any', active: true },
        { label: 'Field: any' },
        { label: 'Active years: any' },
      ]} />

      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
        <thead>
          <tr style={{ borderBottom: `2px solid ${A_INK}` }}>
            {['Member', 'Institution', 'Fields', 'Advised', 'Served on', 'Active span', ''].map(h => (
              <th key={h} style={{ ...aCaps, color: A_MUTE, padding: '14px 24px', textAlign: 'left', fontWeight: 500 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {COMMITTEE.slice(0, 12).map((c, i) => (
            <tr key={c.name} style={{ borderBottom: `1px solid ${A_LINE2}`, background: i % 2 ? 'transparent' : 'rgba(255,255,255,0.4)' }}>
              <td style={{ padding: '14px 24px' }}>
                <a href="#" style={{ ...aSerif, fontSize: 19, fontWeight: 500, color: A_INK, textDecoration: 'none' }}>{c.name}</a>
              </td>
              <td style={{ padding: '14px 24px', fontSize: 13, color: A_INK2 }}>{c.institution}</td>
              <td style={{ padding: '14px 24px' }}>
                <div style={{ display: 'flex', gap: 6 }}>
                  {c.fields.map(f => <span key={f} style={{ ...aMono, fontSize: 11, color: A_INK2, border: `1px solid ${A_LINE}`, padding: '2px 8px', background: A_PAPER3 }}>{f}</span>)}
                </div>
              </td>
              <td style={{ padding: '14px 24px', ...aMono, fontSize: 14, color: A_OX, fontWeight: 600 }}>{c.advised}</td>
              <td style={{ padding: '14px 24px', ...aMono, fontSize: 13, color: A_INK }}>{c.served}</td>
              <td style={{ padding: '14px 24px', ...aMono, fontSize: 12, color: A_INK2 }}>{c.span}</td>
              <td style={{ padding: '14px 24px', textAlign: 'right' }}>
                <a href="#" style={{ ...aCaps, fontSize: 10, color: A_OX, textDecoration: 'none' }}>Lineage →</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <APagination />
    </div>
  );
}

// ── Single dissertation ───────────────────────────────────────
function ADiss() {
  const d = DISSERTATIONS[0];
  return (
    <div style={aRoot}>
      <ANav active="diss" />

      <div style={{ padding: '20px 64px 0', ...aMono, fontSize: 12, color: A_MUTE }}>
        <a href="#" style={{ color: A_MUTE, textDecoration: 'none' }}>Dissertations</a> / {d.id}
      </div>

      <section style={{ padding: '40px 64px 56px', borderBottom: `1px solid ${A_LINE}` }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 64 }}>
          <div>
            <div style={{ ...aCaps, color: A_OX, marginBottom: 16 }}>Dissertation · {d.year}</div>
            <h1 style={{ ...aSerif, fontSize: 44, lineHeight: 1.1, fontWeight: 500, margin: '0 0 24px', letterSpacing: -0.5 }}>{d.title}</h1>
            <div style={{ fontSize: 18, color: A_INK2, ...aSerif }}>
              <em>by</em> <a href="#" style={{ color: A_OX, textDecoration: 'none' }}>{d.author}</a>
              <span style={{ color: A_MUTE, margin: '0 10px' }}>·</span>
              <em>at</em> {d.institution}
            </div>
          </div>
          <aside style={{ borderLeft: `1px solid ${A_LINE}`, paddingLeft: 32 }}>
            <table style={{ fontSize: 13, lineHeight: 1.8, width: '100%' }}>
              <tbody>
                {[
                  ['Record ID', <span style={aMono}>{d.id}</span>],
                  ['Granted', `${d.year}`],
                  ['Institution', d.institution],
                  ['Advisor', <a href="#" style={{ color: A_OX, textDecoration: 'none' }}>{d.advisor}</a>],
                  ['Committee', <span>{d.committee.map((c, i) => <span key={c}>{i > 0 ? ', ' : ''}<a href="#" style={{ color: A_INK, textDecoration: 'underline', textUnderlineOffset: 3 }}>{c}</a></span>)}</span>],
                  ['Field', d.subject],
                  ['Keywords', <span>{d.keywords.map((k, i) => <span key={k} style={{ ...aMono, fontSize: 11, marginRight: 6, color: A_INK2 }}>{k}{i < d.keywords.length - 1 ? ',' : ''}</span>)}</span>],
                ].map(([k, v]) => (
                  <tr key={k}>
                    <td style={{ ...aCaps, color: A_MUTE, paddingRight: 16, verticalAlign: 'top', paddingTop: 6, width: 110 }}>{k}</td>
                    <td style={{ color: A_INK, paddingTop: 6 }}>{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ marginTop: 22, display: 'flex', gap: 10 }}>
              <a href="#" style={{ ...aCaps, padding: '10px 16px', background: A_INK, color: A_PAPER, textDecoration: 'none' }}>Cite this</a>
              <a href="#" style={{ ...aCaps, padding: '10px 16px', border: `1px solid ${A_INK}`, color: A_INK, textDecoration: 'none' }}>Suggest edit</a>
            </div>
          </aside>
        </div>
      </section>

      {/* Abstract */}
      <section style={{ padding: '48px 64px', display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 64, alignItems: 'flex-start' }}>
        <div>
          <div style={{ ...aCaps, color: A_MUTE, marginBottom: 14 }}>Abstract</div>
          <div style={{ ...aSerif, fontSize: 19, lineHeight: 1.65, color: A_INK, columns: 1 }}>
            <p style={{ marginTop: 0 }}>
              <span style={{ float: 'left', ...aSerif, fontSize: 64, lineHeight: 0.85, marginRight: 10, marginTop: 6, color: A_OX, fontWeight: 500 }}>T</span>
              his dissertation reconstructs how dissent took spatial shape in Cold-War Berlin between 1953 and 1989 — not as a series of named protests, but as a slow practice of everyday urban movement: rerouted commutes, contested courtyards, libraries borrowed at odd hours, kitchen-table samizdat.
            </p>
            <p>
              Drawing on Stasi observation logs, neighborhood committee minutes, oral histories recorded in the 1990s, and forty-six unpublished sketchbooks of one apartment-block superintendent, it argues that East and West Berliners produced distinct, mutually legible <em>geographies of refusal</em>.
            </p>
            <p>
              The work intervenes in debates about resistance and the everyday, and proposes a method — <em>cartographic ethnography</em> — for working between Stasi records and personal-archival fragments.
            </p>
          </div>
        </div>
        <aside>
          <div style={{ ...aCaps, color: A_MUTE, marginBottom: 14 }}>Lineage at a glance</div>
          <div style={{ border: `1px solid ${A_LINE}`, padding: 20, background: A_PAPER3 }}>
            <div style={{ ...aMono, fontSize: 11, color: A_MUTE, marginBottom: 4 }}>Advised by</div>
            <div style={{ ...aSerif, fontSize: 20, marginBottom: 14, fontWeight: 500 }}>{d.advisor}</div>
            <div style={{ marginLeft: 18, borderLeft: `2px solid ${A_OX}`, paddingLeft: 16 }}>
              <div style={{ ...aMono, fontSize: 11, color: A_MUTE, marginBottom: 4 }}>Who was advised by</div>
              <div style={{ ...aSerif, fontSize: 16, marginBottom: 12 }}>Helene Voss-Albright</div>
              <div style={{ ...aMono, fontSize: 11, color: A_MUTE, marginBottom: 4 }}>Who was advised by</div>
              <div style={{ ...aSerif, fontSize: 16, color: A_MUTE, fontStyle: 'italic' }}>Hans Möller (1971, Heidelberg)</div>
            </div>
            <a href="#" style={{ ...aCaps, display: 'inline-block', marginTop: 18, color: A_OX, textDecoration: 'none' }}>Open full genealogy →</a>
          </div>
        </aside>
      </section>

      {/* Related */}
      <section style={{ padding: '0 64px 32px' }}>
        <div style={{ ...aCaps, color: A_MUTE, marginBottom: 18 }}>Related dissertations</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 28 }}>
          {[DISSERTATIONS[4], DISSERTATIONS[8], DISSERTATIONS[12]].map(r => (
            <a key={r.id} href="#" style={{ borderTop: `2px solid ${A_INK}`, paddingTop: 16, textDecoration: 'none', color: A_INK }}>
              <div style={{ ...aMono, fontSize: 11, color: A_MUTE, marginBottom: 6 }}>{r.year} · {r.subject}</div>
              <div style={{ ...aSerif, fontSize: 20, lineHeight: 1.25, fontWeight: 500, marginBottom: 8 }}>{r.title}</div>
              <div style={{ fontSize: 13, color: A_INK2, ...aSerif, fontStyle: 'italic' }}>by {r.author}</div>
            </a>
          ))}
        </div>
      </section>

      <AFooter />
    </div>
  );
}

// ── Scholar profile ───────────────────────────────────────────
function AScholar() {
  const s = COMMITTEE[0]; // Helene Voss-Albright — has rich data
  const advised = DISSERTATIONS.filter(d => d.advisor === s.name);
  const served = DISSERTATIONS.filter(d => d.committee.includes(s.name));
  return (
    <div style={aRoot}>
      <ANav active="scholars" />

      <div style={{ padding: '20px 64px 0', ...aMono, fontSize: 12, color: A_MUTE }}>
        <a href="#" style={{ color: A_MUTE, textDecoration: 'none' }}>Scholars</a> / {s.name}
      </div>

      <section style={{ padding: '40px 64px 40px', borderBottom: `1px solid ${A_LINE}` }}>
        <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr auto', gap: 32, alignItems: 'flex-start' }}>
          <div style={{ width: 120, height: 120, borderRadius: 60, background: A_AVATAR, border: `1px solid ${A_LINE}`, display: 'flex', alignItems: 'center', justifyContent: 'center', ...aSerif, fontSize: 40, color: A_OX, fontStyle: 'italic' }}>
            HV
          </div>
          <div>
            <div style={{ ...aCaps, color: A_OX, marginBottom: 10 }}>Committee member · active {s.span}</div>
            <h1 style={{ ...aSerif, fontSize: 52, fontWeight: 500, margin: '0 0 8px', letterSpacing: -0.7 }}>{s.name}</h1>
            <div style={{ fontSize: 17, color: A_INK2, ...aSerif }}>{s.institution} · {s.fields.join(', ')} history</div>
          </div>
          <div style={{ display: 'flex', gap: 24, alignItems: 'flex-end' }}>
            {[
              ['Advised', s.advised], ['Served on', s.served], ['Lineage depth', 4],
            ].map(([k, v]) => (
              <div key={k} style={{ textAlign: 'right' }}>
                <div style={{ ...aSerif, fontSize: 36, fontWeight: 500, color: A_INK, lineHeight: 1 }}>{v}</div>
                <div style={{ ...aCaps, color: A_MUTE, marginTop: 4 }}>{k}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div style={{ display: 'flex', gap: 28, padding: '20px 64px', borderBottom: `1px solid ${A_LINE}`, ...aCaps }}>
        {[['advised', 'Dissertations advised', true], ['served', 'Committees served', false], ['lineage', 'Lineage', false], ['about', 'About', false]].map(([id, label, active]) => (
          <a key={id} href="#" style={{ color: active ? A_OX : A_INK2, textDecoration: 'none', paddingBottom: 4, borderBottom: active ? `2px solid ${A_OX}` : '2px solid transparent' }}>{label}</a>
        ))}
      </div>

      <section style={{ padding: '36px 64px', display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 48 }}>
        <div>
          <div style={{ ...aCaps, color: A_MUTE, marginBottom: 14 }}>14 dissertations advised — recent</div>
          {DISSERTATIONS.slice(0, 6).map((d, i) => (
            <a key={d.id} href="#" style={{ display: 'block', padding: '18px 0', borderBottom: `1px solid ${A_LINE2}`, textDecoration: 'none', color: A_INK }}>
              <div style={{ display: 'flex', gap: 18, alignItems: 'flex-start' }}>
                <div style={{ ...aMono, fontSize: 13, color: A_MUTE, width: 50, paddingTop: 4 }}>{2024 - i * 2}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ ...aSerif, fontSize: 19, lineHeight: 1.3, fontWeight: 500, marginBottom: 4 }}>{d.title}</div>
                  <div style={{ fontSize: 13, color: A_INK2 }}>
                    <span style={{ ...aSerif, fontStyle: 'italic' }}>by</span> {d.author}
                    <span style={{ color: A_MUTE, margin: '0 8px' }}>·</span>
                    {d.institution}
                  </div>
                </div>
                <span style={{ ...aMono, fontSize: 11, color: A_INK2, border: `1px solid ${A_LINE}`, padding: '2px 8px', background: A_PAPER3, flexShrink: 0 }}>{d.subject}</span>
              </div>
            </a>
          ))}
          <a href="#" style={{ display: 'inline-block', marginTop: 18, ...aCaps, color: A_OX, textDecoration: 'none' }}>See all 14 →</a>
        </div>

        <aside>
          <div style={{ border: `1px solid ${A_LINE}`, padding: 24, background: A_PAPER3, marginBottom: 24 }}>
            <div style={{ ...aCaps, color: A_OX, marginBottom: 14 }}>Lineage</div>
            <div style={{ ...aSerif, fontSize: 14, lineHeight: 1.8 }}>
              <div style={{ color: A_MUTE, fontStyle: 'italic', fontSize: 12 }}>advised by</div>
              <div style={{ fontWeight: 500, fontSize: 16 }}>Friedrich Lessing</div>
              <div style={{ paddingLeft: 18, borderLeft: `2px solid ${A_OX}`, marginLeft: 6, marginTop: 8, paddingTop: 6 }}>
                <div style={{ color: A_MUTE, fontStyle: 'italic', fontSize: 12 }}>advised by</div>
                <div style={{ fontSize: 15 }}>Hannah Reinhardt</div>
                <div style={{ color: A_MUTE, fontStyle: 'italic', fontSize: 12, marginTop: 6 }}>advised by</div>
                <div style={{ fontSize: 15, color: A_MUTE }}>Wilhelm Stern (1953)</div>
              </div>
            </div>
            <a href="#" style={{ ...aCaps, display: 'inline-block', marginTop: 18, color: A_OX, textDecoration: 'none' }}>Open visualization →</a>
          </div>

          <div style={{ ...aCaps, color: A_MUTE, marginBottom: 10 }}>Frequent co-readers</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {['J. Sebastian Krüger', 'Anders L. Penrose', 'Eleanor M. Whitcombe', 'Pradeep K. Iyer'].map(n => (
              <a key={n} href="#" style={{ ...aSerif, fontSize: 16, color: A_INK, textDecoration: 'none', display: 'flex', justifyContent: 'space-between', borderBottom: `1px solid ${A_LINE2}`, paddingBottom: 6 }}>
                <span>{n}</span><span style={{ ...aMono, fontSize: 11, color: A_MUTE }}>{Math.floor(Math.random() * 8) + 2}×</span>
              </a>
            ))}
          </div>
        </aside>
      </section>

      <AFooter />
    </div>
  );
}

window.A = { Home: AHome, DissTable: ADissTable, Scholars: AScholars, Committee: ACommittee, Diss: ADiss, Scholar: AScholar };
