// Shared sample data + tiny utilities for all three design directions.
// Names, institutions, titles and dates are fabricated. The shape mirrors
// the live site (dissertations, scholars, committee members, advisors).

const DISSERTATIONS = [
  { id: 'D-2019-0341', title: 'Cartographies of Dissent: Spatial Practices and Urban Resistance in Cold War Berlin, 1953–1989', author: 'Margaret E. Hartwell', institution: 'Yale University', year: 2019, advisor: 'J. Sebastian Krüger', committee: ['Helene Voss-Albright', 'Anders L. Penrose'], subject: 'European / Cold War', keywords: ['Berlin', 'urban history', 'protest', 'spatial theory'] },
  { id: 'D-2021-0078', title: 'The Salted Page: Print Culture and Maritime Labor in the Early Atlantic World, 1680–1740', author: 'Tomás A. Reyes-Mendoza', institution: 'Princeton University', year: 2021, advisor: 'Eleanor M. Whitcombe', committee: ['Harold A. Brackenridge', 'Iris N. Calloway'], subject: 'Atlantic / Early Modern', keywords: ['print', 'sailors', 'labor', 'Atlantic'] },
  { id: 'D-2017-1102', title: 'Reading Weather: Almanacs, Farmers, and Climate Knowledge in the American Midwest, 1890–1935', author: 'Anya Ostrowski', institution: 'University of Wisconsin–Madison', year: 2017, advisor: 'Robert P. Trillin', committee: ['Susan F. Marcourt', 'Daniel B. Olafsson'], subject: 'US / Environmental', keywords: ['weather', 'almanacs', 'agriculture', 'Midwest'] },
  { id: 'D-2020-0224', title: 'Inventing the Bureaucrat: Administrative Labor in Late Qing China, 1860–1911', author: 'Wei-Ming Tan', institution: 'Stanford University', year: 2020, advisor: 'Kathleen S. Hou', committee: ['Pradeep K. Iyer', 'Lin Zhao-Yang'], subject: 'East Asia', keywords: ['Qing', 'bureaucracy', 'labor', 'state'] },
  { id: 'D-2018-0617', title: 'Sound and the Citizen: Public Listening in Weimar Germany', author: 'Klara Eisenberg', institution: 'University of Chicago', year: 2018, advisor: 'J. Sebastian Krüger', committee: ['Margaret E. Hartwell', 'Helene Voss-Albright'], subject: 'European / Cultural', keywords: ['radio', 'Weimar', 'sound studies'] },
  { id: 'D-2016-0903', title: 'Sovereign Distances: Maps and Imperial Imagination in Habsburg Spain', author: 'Diego Salinas-Arroyo', institution: 'Harvard University', year: 2016, advisor: 'Eleanor M. Whitcombe', committee: ['Beatriz C. Llamas', 'Harold A. Brackenridge'], subject: 'Iberian / Empire', keywords: ['cartography', 'Habsburg', 'empire'] },
  { id: 'D-2022-0455', title: 'The Bargain Hour: Women, Department Stores, and Consumer Time, 1895–1925', author: 'Frances H. Whitlock', institution: 'Columbia University', year: 2022, advisor: 'Susan F. Marcourt', committee: ['Robert P. Trillin', 'Cora E. Reinholt'], subject: 'US / Gender', keywords: ['gender', 'consumption', 'labor'] },
  { id: 'D-2019-0810', title: 'Threads of Empire: Indigenous Weavers and the Andean Textile Economy, 1570–1650', author: 'Camila Quispe-Vargas', institution: 'New York University', year: 2019, advisor: 'Beatriz C. Llamas', committee: ['Tomás A. Reyes-Mendoza', 'Iris N. Calloway'], subject: 'Latin America', keywords: ['Andes', 'textiles', 'colonial'] },
  { id: 'D-2015-0297', title: 'The Borrowed Tongue: Translation and Diplomacy in the Ottoman Mediterranean', author: 'Yusuf Demir', institution: 'UC Berkeley', year: 2015, advisor: 'Helene Voss-Albright', committee: ['Anders L. Penrose', 'Pradeep K. Iyer'], subject: 'Middle East / Early Modern', keywords: ['Ottoman', 'translation', 'diplomacy'] },
  { id: 'D-2020-0561', title: 'Pastoralists and Petroleum: Land, Labor, and Energy in Northern Iran, 1908–1979', author: 'Niloufar Behzad', institution: 'University of Michigan', year: 2020, advisor: 'Pradeep K. Iyer', committee: ['Yusuf Demir', 'Helene Voss-Albright'], subject: 'Middle East / Environmental', keywords: ['oil', 'pastoralism', 'Iran'] },
  { id: 'D-2023-0119', title: 'Carrying the Continent: Black Sailors and Atlantic Mobility, 1840–1880', author: 'Jerome A. Lattimer', institution: 'Duke University', year: 2023, advisor: 'Iris N. Calloway', committee: ['Tomás A. Reyes-Mendoza', 'Eleanor M. Whitcombe'], subject: 'Atlantic / Black History', keywords: ['sailors', 'Atlantic', 'mobility'] },
  { id: 'D-2021-0742', title: 'The Hospital and the Hinterland: Tropical Medicine in French West Africa', author: 'Marie-Claire Adoukonou', institution: 'University of Pennsylvania', year: 2021, advisor: 'Cora E. Reinholt', committee: ['Susan F. Marcourt', 'Daniel B. Olafsson'], subject: 'Africa / Medicine', keywords: ['medicine', 'colonial', 'West Africa'] },
  { id: 'D-2014-0508', title: 'Counting the Crown: Census, Taxation, and Statecraft in Tudor England', author: 'Edmund P. Carrow', institution: 'University of Oxford', year: 2014, advisor: 'Anders L. Penrose', committee: ['Helene Voss-Albright', 'Eleanor M. Whitcombe'], subject: 'British / Early Modern', keywords: ['Tudor', 'taxation', 'statecraft'] },
  { id: 'D-2017-0334', title: 'Rivers of Salt: Hydrology and Political Economy in Mughal Bengal', author: 'Suraiya Banerjee', institution: 'Johns Hopkins University', year: 2017, advisor: 'Pradeep K. Iyer', committee: ['Kathleen S. Hou', 'Lin Zhao-Yang'], subject: 'South Asia / Environmental', keywords: ['Mughal', 'water', 'Bengal'] },
  { id: 'D-2019-0628', title: 'The Mended Globe: Repair Craftsmen and the Material Culture of Empire', author: 'Ottilie F. Werner', institution: 'University of Cambridge', year: 2019, advisor: 'Beatriz C. Llamas', committee: ['Anders L. Penrose', 'Iris N. Calloway'], subject: 'Material / Empire', keywords: ['repair', 'craft', 'empire'] },
];

const SCHOLARS = [
  { name: 'Margaret E. Hartwell', institution: 'Yale University', role: 'Assistant Professor', diss: 'D-2019-0341', advised: 0, committee: 1, fields: ['Cold War', 'Urban'] },
  { name: 'Tomás A. Reyes-Mendoza', institution: 'Princeton University', role: 'Postdoctoral Fellow', diss: 'D-2021-0078', advised: 0, committee: 2, fields: ['Atlantic', 'Print'] },
  { name: 'Anya Ostrowski', institution: 'University of Wisconsin–Madison', role: 'Associate Professor', diss: 'D-2017-1102', advised: 1, committee: 0, fields: ['Environmental', 'US'] },
  { name: 'Wei-Ming Tan', institution: 'Stanford University', role: 'Assistant Professor', diss: 'D-2020-0224', advised: 0, committee: 0, fields: ['East Asia'] },
  { name: 'Klara Eisenberg', institution: 'University of Chicago', role: 'Assistant Professor', diss: 'D-2018-0617', advised: 0, committee: 0, fields: ['European', 'Sound'] },
  { name: 'Diego Salinas-Arroyo', institution: 'Harvard University', role: 'Associate Professor', diss: 'D-2016-0903', advised: 2, committee: 1, fields: ['Iberian', 'Empire'] },
  { name: 'Frances H. Whitlock', institution: 'Columbia University', role: 'Lecturer', diss: 'D-2022-0455', advised: 0, committee: 0, fields: ['US', 'Gender'] },
  { name: 'Camila Quispe-Vargas', institution: 'New York University', role: 'Assistant Professor', diss: 'D-2019-0810', advised: 0, committee: 0, fields: ['Latin America'] },
  { name: 'Yusuf Demir', institution: 'UC Berkeley', role: 'Associate Professor', diss: 'D-2015-0297', advised: 3, committee: 2, fields: ['Ottoman', 'Mediterranean'] },
  { name: 'Niloufar Behzad', institution: 'University of Michigan', role: 'Assistant Professor', diss: 'D-2020-0561', advised: 0, committee: 0, fields: ['Middle East'] },
  { name: 'Jerome A. Lattimer', institution: 'Duke University', role: 'ABD', diss: 'D-2023-0119', advised: 0, committee: 0, fields: ['Atlantic', 'Black History'] },
  { name: 'Marie-Claire Adoukonou', institution: 'University of Pennsylvania', role: 'Assistant Professor', diss: 'D-2021-0742', advised: 0, committee: 0, fields: ['Africa', 'Medicine'] },
];

// Committee-side scholars (mostly senior, not always with diss in this DB).
const COMMITTEE = [
  { name: 'Helene Voss-Albright', institution: 'Yale University', advised: 14, served: 38, span: '1992–2024', fields: ['European', 'Diplomatic'] },
  { name: 'J. Sebastian Krüger', institution: 'Yale University', advised: 11, served: 27, span: '1996–2024', fields: ['European', 'Cold War'] },
  { name: 'Eleanor M. Whitcombe', institution: 'Princeton University', advised: 9, served: 22, span: '2000–2024', fields: ['Atlantic', 'Early Modern'] },
  { name: 'Robert P. Trillin', institution: 'Wisconsin–Madison', advised: 16, served: 41, span: '1988–2022', fields: ['US', 'Environmental'] },
  { name: 'Pradeep K. Iyer', institution: 'University of Michigan', advised: 8, served: 19, span: '2002–2024', fields: ['South Asia', 'Empire'] },
  { name: 'Kathleen S. Hou', institution: 'Stanford University', advised: 7, served: 14, span: '2005–2024', fields: ['East Asia'] },
  { name: 'Anders L. Penrose', institution: 'University of Oxford', advised: 12, served: 33, span: '1994–2023', fields: ['British', 'Early Modern'] },
  { name: 'Beatriz C. Llamas', institution: 'Harvard University', advised: 10, served: 21, span: '1999–2024', fields: ['Iberian', 'Material'] },
  { name: 'Susan F. Marcourt', institution: 'Wisconsin–Madison', advised: 6, served: 17, span: '2003–2024', fields: ['US', 'Gender'] },
  { name: 'Harold A. Brackenridge', institution: 'Princeton University', advised: 5, served: 14, span: '2001–2024', fields: ['Atlantic', 'Imperial'] },
  { name: 'Iris N. Calloway', institution: 'Princeton University', advised: 4, served: 12, span: '2008–2024', fields: ['Atlantic', 'Black History'] },
  { name: 'Cora E. Reinholt', institution: 'University of Pennsylvania', advised: 3, served: 9, span: '2011–2024', fields: ['Medicine', 'Africa'] },
  { name: 'Daniel B. Olafsson', institution: 'Wisconsin–Madison', advised: 4, served: 10, span: '2009–2024', fields: ['US', 'Environmental'] },
  { name: 'Lin Zhao-Yang', institution: 'Stanford University', advised: 6, served: 13, span: '2004–2024', fields: ['East Asia'] },
  { name: 'Ottilie F. Werner', institution: 'University of Cambridge', advised: 2, served: 5, span: '2014–2024', fields: ['Material', 'Empire'] },
];

// Tiny deterministic hash → small int. Used by the Ledger direction for
// per-record sigils so the same record always renders the same glyph.
function hashStr(s) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = (h * 16777619) >>> 0; }
  return h >>> 0;
}

// 4×4 sigil — 8 random cells filled, symmetric L/R. Returns array of {x,y} in 0..3.
function sigil(seed, size = 4, count = 7) {
  const cells = [];
  let h = seed;
  const used = new Set();
  while (cells.length < count) {
    h = (h * 1103515245 + 12345) >>> 0;
    const x = h % (size / 2 | 0);
    h = (h * 1103515245 + 12345) >>> 0;
    const y = h % size;
    const key = x + ',' + y;
    if (used.has(key)) continue;
    used.add(key);
    cells.push({ x, y });
    cells.push({ x: size - 1 - x, y });
  }
  return cells;
}

// Simple SVG component placeholder for "diss callout sigil".
function Sigil({ seed, size = 14, color = '#1a1a1a', cell = 3, gap = 1 }) {
  const grid = 4;
  const cells = sigil(typeof seed === 'string' ? hashStr(seed) : seed, grid);
  const w = grid * cell + (grid - 1) * gap;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${w} ${w}`}>
      {cells.map((c, i) => (
        <rect key={i} x={c.x * (cell + gap)} y={c.y * (cell + gap)} width={cell} height={cell} fill={color} />
      ))}
    </svg>
  );
}

Object.assign(window, { DISSERTATIONS, SCHOLARS, COMMITTEE, hashStr, sigil, Sigil });
