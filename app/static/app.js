/* Fitness & Diet – Oberfläche (Vanilla JS) */
const $ = (s, el = document) => el.querySelector(s);
const view = $('#view');
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const api = async (p, opt = {}) => {
  const r = await fetch('/api/' + p, { headers: { 'Content-Type': 'application/json' }, ...opt });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
};
const iso = d => new Date(d.getTime() - d.getTimezoneOffset() * 6e4).toISOString().slice(0, 10);
const addDays = (s, n) => { const d = new Date(s + 'T12:00:00'); d.setDate(d.getDate() + n); return iso(d); };
const fmt = s => new Date(s + 'T12:00:00').toLocaleDateString('de-DE', { day: 'numeric', month: 'long' });
const TICK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';
const STATUS = { plan: ['Im Plan', ''], frei: ['Passt', ''], vorsicht: ['Vorsicht', 'warn'], spaeter: ['Später', 'grey'], nein: ['Aktuell nein', 'danger'] };

const S = { tab: 'today', day: iso(new Date()), cfg: null, ex: null, exById: {}, rc: null, rcBySlug: {}, sup: null,
  exFilter: { q: '', status: 'plan', group: '' }, rcFilter: '' };

async function boot() {
  [S.cfg, S.ex, S.rc, S.sup] = await Promise.all([api('config'), api('exercises'), api('recipes'), api('supplements')]);
  S.ex.forEach(e => S.exById[e.id] = e);
  S.rc.forEach(r => S.rcBySlug[r.slug] = r);
  if (S.day < S.cfg.start && iso(new Date()) < S.cfg.start) S.day = iso(new Date());
  const h = location.hash.slice(1); if (h) S.tab = h;
  render();
}
document.addEventListener('click', e => {
  const t = e.target.closest('[data-tab]');
  if (t) { S.tab = t.dataset.tab; location.hash = S.tab; render(); window.scrollTo(0, 0); }
});
$('#modal').addEventListener('click', e => { if (e.target.id === 'modal' || e.target.closest('.close')) closeModal(); });
function openModal(html) { $('#modal-body').innerHTML = html; $('#modal').classList.remove('hidden'); document.body.style.overflow = 'hidden'; }
function closeModal() { $('#modal').classList.add('hidden'); document.body.style.overflow = ''; clearInterval(S.animT); }

function render() {
  document.querySelectorAll('nav.tabs button').forEach(b => b.classList.toggle('active', b.dataset.tab === S.tab));
  ({ today: renderToday, week: renderWeek, exercises: renderExercises, recipes: renderRecipes, supps: renderSupps,
     stats: renderStats, settings: renderSettings }[S.tab] || renderToday)();
}

/* ------------------------------------------------------------ Bausteine */
const img = p => '/img/ex/' + p;
const mealieImg = r => `${S.cfg.mealie}/api/media/recipes/${r.id}/images/min-original.webp`;
function exThumb(e) {
  return e.images?.length ? `<img loading="lazy" src="${img(e.images[0])}" alt="">` : `<div class="ph">${esc(e.id.startsWith('K') || e.id.startsWith('N') ? e.id : '')}</div>`;
}
function recipeCard(slug, label = '') {
  const r = S.rcBySlug[slug]; if (!r) return '';
  return `<div class="rcard" data-recipe="${esc(slug)}"><img loading="lazy" src="${mealieImg(r)}" alt="" onerror="this.style.visibility='hidden'">
    <div><div class="n">${esc(r.name)}</div><div class="small muted">${label ? esc(label) + ' · ' : ''}${esc(r.time || '')}</div></div></div>`;
}
function suppList(when, d3k2) {
  return S.sup.current.filter(s => s.when === when && s.status !== 'pause')
    .filter(s => !s.name.startsWith('Vitamin D3') || d3k2)
    .map(s => `<li><b>${esc(s.name)}</b> – ${esc(s.dose)}${s.status === 'prüfen' || s.status === 'arzt' ? ' <span class="badge warn">prüfen</span>' : ''}</li>`).join('');
}

/* ------------------------------------------------------------ Heute */
async function renderToday() {
  const d = await api('day/' + S.day);
  S.d = d;
  const log = d.log || {}; const done = log.done || {}; const exDone = log.ex || {};
  const isToday = S.day === iso(new Date());
  const pct = d.score.total ? Math.round(100 * d.score.done / d.score.total) : 0;
  const set = S.cfg.settings;
  let h = `<div class="daynav"><button class="btn small" id="prev">‹</button>
    <h2>${d.weekday}, ${fmt(d.date)}<span class="sub">${isToday ? 'Heute · ' : ''}${d.week ? 'Woche ' + d.week + ' · ' : ''}Phase: ${esc(d.phase_name)}</span></h2>
    <button class="btn small" id="next">›</button></div>`;
  if (!isToday) h += `<div style="text-align:center;margin:-4px 0 10px"><button class="btn small" id="gotoday">Zu heute</button></div>`;
  if (!set.doctor_ok) h += `<div class="banner warn">Vorsichtsmodus: Arzt- und Physio-Freigabe fehlt noch. Nur die Start-Einheiten, kurze Wege, und bei Schmerzen abbrechen.</div>`;
  if (d.hold) h += `<div class="banner danger">Bremse aktiv: In den letzten 7 Tagen war ein Schmerzwert ≥ 5/10. Der Plan bleibt eine Stufe tiefer. Bei anhaltenden Beschwerden: ärztlich abklären.</div>`;
  h += `<div class="card"><div class="row between"><div class="row"><span class="badge">${esc(d.location_label)}</span>
      <span class="badge ${d.alcohol.startsWith('Kein') ? 'danger' : 'grey'}">${esc(d.alcohol)}</span>${d.d3k2 ? '<span class="badge warn">D3+K2-Tag</span>' : ''}</div>
      <b>${d.score.done}/${d.score.total}</b></div>
    <div class="progress"><div style="width:${pct}%"></div></div>
    <div class="small muted">💡 ${esc(d.tip)}</div></div>`;
  if (d.tasks.length) h += `<div class="card"><h3>Aufgaben diese Woche</h3>${d.tasks.map((t, i) => `<label class="row" style="margin:.25rem 0">
      <input type="checkbox" data-task="${i}" ${log.tasks?.[i] ? 'checked' : ''} style="width:20px;height:20px;accent-color:var(--accent)"> ${esc(t)}</label>`).join('')}</div>`;

  for (const b of d.blocks) {
    let body = '';
    if (b.workout) {
      body += `<div class="exlist">${b.workout.items.map((it, i) => {
        const e = S.exById[it.ex] || { id: it.ex, name: it.ex, images: [] };
        const k = b.id + ':' + i;
        return `<div class="exitem" data-ex="${esc(e.id)}">${exThumb(e)}<div><div class="n">${esc(e.name)}${it.extra ? ' <span class="badge">+</span>' : ''}</div>
          <div class="d">${esc(it.dose)}</div></div><input type="checkbox" data-exk="${esc(k)}" ${exDone[k] ? 'checked' : ''} aria-label="erledigt"></div>`;
      }).join('')}</div>`;
    } else if (b.ex) {
      body += `<div class="exlist">${b.ex.map(id => { const e = S.exById[id]; return e ? `<div class="exitem" data-ex="${id}">${exThumb(e)}<div><div class="n">${esc(e.name)}</div><div class="d">${esc(e.start || '')}</div></div><span></span></div>` : ''; }).join('')}</div>`;
    }
    if (b.recipe) {
      body += recipeCard(b.recipe) + `<div class="row" style="margin-top:.4rem"><button class="btn small" data-swap="${b.id}">Anderes Rezept</button>
        ${d.recipe_tips[b.recipe] ? `<span class="small muted">${esc(d.recipe_tips[b.recipe])}</span>` : ''}</div>`;
    }
    if (b.side) body += `<div class="small muted" style="margin-top:.3rem">Beilagen-Idee:</div>` + recipeCard(b.side, 'Beilage');
    if (b.supp) body += `<ul class="clean small">${suppList(b.supp, d.d3k2)}</ul><div class="small muted">MSM pausiert (siehe Supps).</div>`;
    if (b.metric) body += `<div class="row" style="margin-top:.4rem"><input type="number" step="0.1" inputmode="decimal" data-metric="${b.metric}"
        value="${log[b.metric] ?? ''}" placeholder="${b.metric === 'weight' ? 'kg' : 'cm'}" style="max-width:130px"> <span class="muted">${b.metric === 'weight' ? 'kg' : 'cm'}</span></div>`;
    const canTick = b.kind !== 'event';
    h += `<div class="block ${b.kind} ${done[b.id] ? 'done' : ''}"><div class="time">${esc(b.time)}</div>
      <div><div class="btitle">${esc(b.title)}${b.optional ? ' <span class="badge grey">optional</span>' : ''}</div>
      ${b.text ? `<div class="btext">${esc(b.text)}</div>` : ''}${body}</div>
      ${canTick ? `<button class="tick ${done[b.id] ? 'on' : ''}" data-done="${b.id}" aria-label="erledigt">${TICK}</button>` : '<span></span>'}</div>`;
  }

  const n = d.nutrition;
  h += `<div class="card"><div class="row between"><h3>Ernährung (Yazio)</h3><span class="small muted">${n ? 'importiert' : 'noch kein Import'}</span></div>
    ${n ? `<div class="two"><div class="stat"><div class="v">${Math.round(n.kcal || 0)}</div><div class="l">kcal von ${set.kcal_target}</div></div>
      <div class="stat"><div class="v">${n.protein == null ? '–' : Math.round(n.protein) + ' g'}</div><div class="l">Eiweiß von ${set.protein_target} g</div></div></div>
      <div class="progress"><div style="width:${Math.min(100, 100 * (n.kcal || 0) / set.kcal_target)}%"></div></div>`
      : `<div class="small muted">Kommt automatisch per iPhone-Kurzbefehl aus Apple Health – Anleitung unter ⚙️.</div>`}</div>`;

  const pain = log.pain || {};
  h += `<div class="card"><h3>Tagescheck</h3>
    ${['Achilles', 'Knie', 'Nacken', 'Bauch'].map(k => `<div class="pain"><span>${k}</span>
      <input type="range" min="0" max="10" value="${pain[k] ?? 0}" data-pain="${k}"><b id="pv-${k}">${pain[k] ?? 0}</b></div>`).join('')}
    <div class="two"><div><label class="f">Energie (1–5)</label><input type="number" min="1" max="5" data-field="energy" value="${log.energy ?? ''}"></div>
    <div><label class="f">Alkohol (Gläser)</label><input type="number" min="0" data-field="drinks" value="${log.drinks ?? ''}"></div></div>
    <label class="f">Notiz</label><textarea rows="2" data-field="note" placeholder="Wie lief's? Was hat gezwickt?">${esc(log.note || '')}</textarea>
    <div class="small muted" style="margin-top:.4rem">Schmerz ≥ 5 oder schlechter als gestern → morgen nur Mobilität und Gehen. Abbrechen bei Brustdruck, Atemnot, Schwindel, einseitiger Beinschwellung oder zunehmenden Bauchschmerzen.</div></div>`;
  view.innerHTML = h;

  const save = async patch => { Object.assign(log, patch); await api('log/' + S.day, { method: 'PUT', body: JSON.stringify(patch) }); };
  $('#prev').onclick = () => { S.day = addDays(S.day, -1); renderToday(); };
  $('#next').onclick = () => { S.day = addDays(S.day, 1); renderToday(); };
  $('#gotoday') && ($('#gotoday').onclick = () => { S.day = iso(new Date()); renderToday(); });
  view.querySelectorAll('[data-done]').forEach(b => b.onclick = async () => {
    done[b.dataset.done] = !done[b.dataset.done]; await save({ done }); renderToday();
  });
  view.querySelectorAll('[data-exk]').forEach(c => { c.onclick = e => e.stopPropagation(); c.onchange = async () => {
    exDone[c.dataset.exk] = c.checked;
    const bid = c.dataset.exk.split(':')[0]; const blk = d.blocks.find(x => x.id === bid);
    const all = blk.workout.items.every((_, i) => exDone[bid + ':' + i]);
    if (all && !done[bid]) { done[bid] = true; await save({ ex: exDone, done }); return renderToday(); }
    await save({ ex: exDone });
  }; });
  view.querySelectorAll('[data-task]').forEach(c => c.onchange = () => { const t = log.tasks || {}; t[c.dataset.task] = c.checked; save({ tasks: t }); });
  view.querySelectorAll('[data-metric]').forEach(i => i.onchange = () => save({ [i.dataset.metric]: i.value ? +i.value : null }));
  view.querySelectorAll('[data-field]').forEach(i => i.onchange = () => save({ [i.dataset.field]: i.type === 'number' ? (i.value ? +i.value : null) : i.value }));
  view.querySelectorAll('[data-pain]').forEach(i => {
    i.oninput = () => $('#pv-' + i.dataset.pain).textContent = i.value;
    i.onchange = () => { pain[i.dataset.pain] = +i.value; save({ pain }); };
  });
  view.querySelectorAll('[data-ex]').forEach(x => x.onclick = () => showExercise(x.dataset.ex));
  view.querySelectorAll('[data-recipe]').forEach(x => x.onclick = () => showRecipe(x.dataset.recipe));
  view.querySelectorAll('[data-swap]').forEach(btn => btn.onclick = async () => {
    const b = d.blocks.find(x => x.id === btn.dataset.swap); const cur = S.rcBySlug[b.recipe];
    const pool = S.rc.filter(r => r.cat === cur.cat || (['koch', 'mittag', 'suppe'].includes(cur.cat) && ['koch', 'mittag', 'suppe'].includes(r.cat)));
    const nxt = pool[(pool.findIndex(r => r.slug === b.recipe) + 1 + Math.floor(Math.random() * (pool.length - 1))) % pool.length];
    const swap = log.swap || {}; swap[b.id] = nxt.slug; await save({ swap }); renderToday();
  });
}

/* ------------------------------------------------------------ Woche */
async function renderWeek() {
  const w = await api('week/' + S.day);
  const today = iso(new Date());
  let h = `<div class="daynav"><button class="btn small" id="prev">‹</button><h2>${w.week >= 1 ? 'Woche ' + w.week : 'Vorwoche'}
    <span class="sub">${fmt(w.monday)} – ${fmt(addDays(w.monday, 6))}</span></h2><button class="btn small" id="next">›</button></div>`;
  if (w.tasks.length) h += `<div class="card"><h3>Aufgaben</h3><ul class="clean">${w.tasks.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div>`;
  for (const d of w.days) {
    const wo = d.blocks.filter(b => b.kind === 'workout' || b.kind === 'walk').map(b => b.title.replace('Optional: ', '(opt.) '));
    const meals = d.blocks.filter(b => b.meal && b.recipe).map(b => S.rcBySlug[b.recipe]?.name).filter(Boolean);
    const ev = d.blocks.filter(b => b.kind === 'event').map(b => b.title);
    h += `<div class="card wday ${d.date === today ? 'today' : ''}" data-day="${d.date}"><div class="d">${d.weekday.slice(0, 2)}<small>${d.date.slice(8)}.${d.date.slice(5, 7)}.</small></div>
      <div><div class="row between"><span class="badge">${esc(d.location_label)}</span><span class="small muted">${d.score.done}/${d.score.total}</span></div>
      <div class="wline"><b>Bewegung:</b> ${esc(wo.join(' · ') || '—')}</div>
      ${meals.length ? `<div class="wline"><b>Kochen:</b> ${esc(meals.join(' · '))}</div>` : ''}
      ${ev.length ? `<div class="wline"><b>Termine:</b> ${esc(ev.join(' · '))}</div>` : ''}</div></div>`;
  }
  view.innerHTML = h;
  $('#prev').onclick = () => { S.day = addDays(S.day, -7); renderWeek(); };
  $('#next').onclick = () => { S.day = addDays(S.day, 7); renderWeek(); };
  view.querySelectorAll('[data-day]').forEach(x => x.onclick = () => { S.day = x.dataset.day; S.tab = 'today'; location.hash = 'today'; render(); });
}

/* ------------------------------------------------------------ Übungen */
function renderExercises() {
  const f = S.exFilter;
  const groups = [...new Set(S.ex.map(e => e.group))];
  const list = S.ex.filter(e => (!f.status || e.status === f.status) && (!f.group || e.group === f.group) &&
    (!f.q || (e.name + ' ' + e.id + ' ' + e.equip).toLowerCase().includes(f.q.toLowerCase())));
  view.innerHTML = `<input type="search" id="q" placeholder="Übung suchen …" value="${esc(f.q)}" style="margin-bottom:10px">
    <div class="chips">${[['', 'Alle'], ...Object.entries(STATUS).map(([k, v]) => [k, v[0]])].map(([k, l]) => `<button class="chip ${f.status === k ? 'on' : ''}" data-st="${k}">${l}</button>`).join('')}</div>
    <div class="chips">${['', ...groups].map(g => `<button class="chip ${f.group === g ? 'on' : ''}" data-gr="${esc(g)}">${esc(g || 'Alle Bereiche')}</button>`).join('')}</div>
    <div class="small muted" style="margin-bottom:8px">${list.length} Übungen. K = deine Karten, N = Zusatzkarten, Rest: free-exercise-db (Anleitung englisch).</div>
    <div class="grid">${list.map(e => `<div class="tile" data-ex="${esc(e.id)}">${e.images?.length ? `<img loading="lazy" src="${img(e.images[0])}" alt="">` : `<div class="ph">${esc(e.id)}</div>`}
      <div class="body"><div class="n">${esc(e.name)}</div><div class="row" style="margin-top:4px"><span class="badge ${STATUS[e.status][1]}">${STATUS[e.status][0]}</span><span class="small muted">${esc(e.equip)}</span></div></div></div>`).join('')}</div>`;
  const q = $('#q'); q.oninput = () => { f.q = q.value; const p = q.selectionStart; renderExercises(); const n = $('#q'); n.focus(); n.setSelectionRange(p, p); };
  view.querySelectorAll('[data-st]').forEach(c => c.onclick = () => { f.status = c.dataset.st; renderExercises(); });
  view.querySelectorAll('[data-gr]').forEach(c => c.onclick = () => { f.group = c.dataset.gr; renderExercises(); });
  view.querySelectorAll('[data-ex]').forEach(x => x.onclick = () => showExercise(x.dataset.ex));
}
function showExercise(id) {
  const e = S.exById[id]; if (!e) return;
  const st = STATUS[e.status];
  openModal(`<h2>${esc(e.name)}</h2><div class="row"><span class="badge ${st[1]}">${st[0]}</span><span class="badge grey">${esc(e.group)}</span><span class="badge grey">${esc(e.equip)}</span></div>
    ${e.images?.length ? `<div class="anim">${e.images.map((p, i) => `<img src="${img(p)}" alt="" style="opacity:${i ? 0 : 1}">`).join('')}</div>${e.img_note ? `<div class="small muted">${esc(e.img_note)}</div>` : ''}` : ''}
    ${e.warn ? `<div class="banner ${e.status === 'nein' ? 'danger' : 'warn'}" style="margin-top:.5rem">${esc(e.warn)}</div>` : ''}
    ${e.start ? `<p><b>Start:</b> ${esc(e.start)}</p>` : ''}
    <h3>Anleitung${e.lang === 'en' ? ' (englisch)' : ''}</h3><ol class="steps">${e.steps.map(s => `<li>${esc(s)}</li>`).join('')}</ol>
    ${e.cues?.length ? `<h3>Achte auf</h3><ul class="clean">${e.cues.map(s => `<li>${esc(s)}</li>`).join('')}</ul>` : ''}
    <p class="small muted">Quelle: ${esc(e.source)}</p>`);
  const imgs = document.querySelectorAll('.anim img');
  clearInterval(S.animT);
  if (imgs.length > 1) { let i = 0; S.animT = setInterval(() => { imgs[i].style.opacity = 0; i = (i + 1) % imgs.length; imgs[i].style.opacity = 1; }, 1100); }
}

/* ------------------------------------------------------------ Rezepte */
const RCAT = { koch: 'Kochabend', mittag: 'Mittag', suppe: 'Suppen', salat: 'Salate', beilage: 'Beilagen', fruehstueck: 'Frühstück', brot: 'Brot', snack: 'Snacks' };
function renderRecipes() {
  const list = S.rc.filter(r => !S.rcFilter || r.cat === S.rcFilter);
  view.innerHTML = `<div class="chips">${[['', 'Alle'], ...Object.entries(RCAT)].map(([k, l]) => `<button class="chip ${S.rcFilter === k ? 'on' : ''}" data-c="${k}">${l}</button>`).join('')}</div>
    <div class="small muted" style="margin-bottom:8px">${list.length} ausgewählte Rezepte aus deinem Mealie – leicht, eiweißreich, viel Gemüse.</div>
    <div class="grid">${list.map(r => `<div class="tile" data-recipe="${esc(r.slug)}"><img loading="lazy" src="${mealieImg(r)}" alt="" onerror="this.style.visibility='hidden'">
      <div class="body"><div class="n">${esc(r.name)}</div><div class="small muted">${esc(RCAT[r.cat])} · ${esc(r.time)}</div></div></div>`).join('')}</div>`;
  view.querySelectorAll('[data-c]').forEach(c => c.onclick = () => { S.rcFilter = c.dataset.c; renderRecipes(); });
  view.querySelectorAll('[data-recipe]').forEach(x => x.onclick = () => showRecipe(x.dataset.recipe));
}
function showRecipe(slug) {
  const r = S.rcBySlug[slug]; if (!r) return;
  const tip = S.d?.recipe_tips?.[slug];
  openModal(`<h2>${esc(r.name)}</h2><div class="row"><span class="badge">${esc(RCAT[r.cat])}</span><span class="badge grey">${esc(r.time)}</span>${r.servings ? `<span class="badge grey">${esc(r.servings)} Portionen</span>` : ''}</div>
    <img class="hero" src="${mealieImg(r)}" alt="" onerror="this.remove()">
    ${tip ? `<div class="banner ok">Coach-Tipp: ${esc(tip)}</div>` : ''}
    <div class="banner ok">Portion: halber Teller Gemüse, ein Viertel Eiweiß, ein Viertel Beilage.</div>
    <h3>Zutaten</h3><ul class="clean">${r.ingredients.map(i => `<li>${esc(i)}</li>`).join('')}</ul>
    <h3>Zubereitung</h3><ol class="steps">${r.steps.map(s => `<li>${esc(s)}</li>`).join('')}</ol>
    <a class="btn primary" href="${S.cfg.mealie}/g/home/r/${esc(slug)}" target="_blank" rel="noopener">In Mealie öffnen</a>`);
}

/* ------------------------------------------------------------ Supplements */
function renderSupps() {
  const s = S.sup;
  const cls = { weiter: '', 'prüfen': 'warn', pause: 'danger', arzt: 'warn' };
  view.innerHTML = `<div class="banner danger">${esc(s.alert)}</div><div class="card"><p style="margin:0">${esc(s.intro)}</p></div>
    <h3>Deine aktuellen Mittel</h3>${s.current.map(c => `<div class="card"><div class="row between"><b>${esc(c.name)}</b><span class="badge ${cls[c.status]}">${esc(c.status)}</span></div>
      <div class="small"><b>${esc(c.dose)}</b>${c.when !== '-' ? ' · ' + (c.when === 'morning' ? 'morgens' : 'abends') : ''}</div><div class="small muted">${esc(c.note)}</div></div>`).join('')}
    <h3>Vergleiche</h3>${s.compare.map(c => `<div class="card"><h3>${esc(c.title)}</h3><div class="banner ok" style="margin-bottom:.5rem">${esc(c.verdict)}</div><div class="small">${esc(c.text)}</div></div>`).join('')}
    <h3>Fahrplan</h3>${s.plan.map(p => `<div class="card"><b>${esc(p.phase)}</b><ul class="clean small">${p.items.map(i => `<li>${esc(i)}</li>`).join('')}</ul></div>`).join('')}
    <div class="card"><h3>Fragen an den Hausarzt</h3><ol class="steps small">${s.doctor.map(i => `<li>${esc(i)}</li>`).join('')}</ol></div>
    <div class="card small"><b>Quellen</b><ul class="clean">${s.sources.map(x => `<li><a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.title)}</a></li>`).join('')}</ul>
    <div class="muted">Keine medizinische Beratung – Grundlage für das Arztgespräch.</div></div>`;
}

/* ------------------------------------------------------------ Verlauf */
function lineChart(points, unit) {
  if (points.length < 2) return '<div class="small muted">Noch zu wenige Werte – trag jeden Montag dein Gewicht ein.</div>';
  const W = 600, H = 170, P = 26;
  const xs = points.map(p => new Date(p.x + 'T12:00:00').getTime()), ys = points.map(p => p.y);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys) - 1, y1 = Math.max(...ys) + 1;
  const X = x => P + (W - 2 * P) * (x - x0) / (x1 - x0 || 1), Y = y => H - P - (H - 2 * P) * (y - y0) / (y1 - y0 || 1);
  const d = points.map((p, i) => `${i ? 'L' : 'M'}${X(xs[i]).toFixed(1)},${Y(p.y).toFixed(1)}`).join(' ');
  return `<svg class="chart" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><path d="${d}" fill="none" stroke="var(--accent)" stroke-width="2.5"/>
    ${points.map((p, i) => `<circle cx="${X(xs[i])}" cy="${Y(p.y)}" r="3.5" fill="var(--accent)"/>`).join('')}
    <text x="${P}" y="12">${y1.toFixed(0)} ${unit}</text><text x="${P}" y="${H - 6}">${y0.toFixed(0)} ${unit}</text></svg>`;
}
async function renderStats() {
  const st = await api('stats');
  const w = st.series.filter(s => s.weight).map(s => ({ x: s.day, y: s.weight }));
  const wa = st.series.filter(s => s.waist).map(s => ({ x: s.day, y: s.waist }));
  const first = w[0]?.y, last = w[w.length - 1]?.y;
  const nut = st.nutrition.slice(-14);
  const avg = nut.length ? Math.round(nut.reduce((a, n) => a + (n.kcal || 0), 0) / nut.length) : null;
  view.innerHTML = `<div class="card"><div class="two">
      <div class="stat"><div class="v">🔥 ${st.streak}</div><div class="l">Tage in Folge ≥ 60 % erledigt</div></div>
      <div class="stat"><div class="v">${first && last ? (last - first > 0 ? '+' : '') + (last - first).toFixed(1) + ' kg' : '–'}</div><div class="l">seit Start${last ? ' · aktuell ' + last + ' kg' : ''}</div></div></div></div>
    <div class="card"><h3>Gewicht</h3>${lineChart(w, 'kg')}</div>
    <div class="card"><h3>Bauchumfang</h3>${lineChart(wa, 'cm')}</div>
    <div class="card"><h3>Ernährung (Yazio, 14 Tage)</h3>${nut.length ? `<div class="small muted">Ø ${avg} kcal/Tag</div>
      <table class="t"><tr><th>Tag</th><th>kcal</th><th>Eiweiß</th></tr>${nut.slice().reverse().map(n => `<tr><td>${fmt(n.day)}</td><td>${Math.round(n.kcal || 0)}</td><td>${n.protein == null ? '–' : Math.round(n.protein) + ' g'}</td></tr>`).join('')}</table>`
      : '<div class="small muted">Noch keine Daten – Kurzbefehl einrichten (⚙️).</div>'}</div>
    <div class="card"><h3>Schmerz-Tagebuch</h3><table class="t"><tr><th>Tag</th><th>Achilles</th><th>Knie</th><th>Nacken</th><th>Bauch</th></tr>
      ${st.series.filter(s => Object.keys(s.pain || {}).length).slice(-14).reverse().map(s => `<tr><td>${fmt(s.day)}</td>${['Achilles', 'Knie', 'Nacken', 'Bauch'].map(k => `<td>${s.pain[k] ?? '–'}</td>`).join('')}</tr>`).join('') || '<tr><td colspan="5" class="muted">Noch keine Einträge</td></tr>'}</table></div>`;
}

/* ------------------------------------------------------------ Einstellungen */
function renderSettings() {
  const s = S.cfg.settings;
  const opt = (v, cur, l) => `<option value="${v}" ${String(v) === String(cur) ? 'selected' : ''}>${l}</option>`;
  const url = location.origin + '/api/nutrition';
  view.innerHTML = `<h2>Einstellungen</h2>
    <div class="card"><h3>Training</h3>
      <label class="f">Krafttage pro Woche</label><select id="sd">${opt(2, s.strength_days, '2 × (Mo, Mi) – Start')}${opt(3, s.strength_days, '3 × (+ Sa vormittags)')}${opt(4, s.strength_days, '4 × (+ Do fix, Sa)')}</select>
      <label class="f">Dauer pro Einheit</label><select id="mi">${opt(20, s.minutes, '20 Min. – Start')}${opt(30, s.minutes, '30 Min. (+2 Übungen)')}${opt(45, s.minutes, '45 Min. (+4 Übungen, mehr Sätze)')}</select>
      <label class="f">Stufe</label><select id="lv">${opt('auto', s.level, 'Automatisch nach Woche')}${opt(1, s.level, '1 – Eingewöhnen')}${opt(2, s.level, '2 – Aufbauen')}${opt(3, s.level, '3 – Festigen')}</select>
      <div class="small muted" style="margin-top:.4rem">Zusatzübungen kommen nur aus „Im Plan“/„Passt“ und erst ab Stufe 2. Die Schmerz-Bremse gilt immer.</div>
      <label class="row" style="margin-top:.7rem"><input type="checkbox" id="doc" ${s.doctor_ok ? 'checked' : ''} style="width:20px;height:20px;accent-color:var(--accent)"> Arzt/Physio hat das Programm freigegeben</label></div>
    <div class="card"><h3>Ziele</h3><div class="two"><div><label class="f">kcal / Tag</label><input type="number" id="kc" value="${s.kcal_target}"></div>
      <div><label class="f">Eiweiß g / Tag</label><input type="number" id="pr" value="${s.protein_target}"></div></div>
      <div class="small muted" style="margin-top:.4rem">Startwert: ca. 2.200 kcal und 140 g Eiweiß (moderates Defizit). Das genaue Ziel stellst du in Yazio ein und überträgst es hierher.</div></div>
    <button class="btn primary" id="save">Speichern</button> <span id="saved" class="small muted"></span>
    <div class="card" style="margin-top:12px"><h3>Yazio → App (iPhone-Kurzbefehl)</h3>
      <div class="small">Yazio hat keine offene Schnittstelle, schreibt aber Kalorien und Makros in <b>Apple Health</b> (in Yazio: Profil → Einstellungen → Apps & Geräte → Apple Health → „Ernährung“ schreiben). Der Kurzbefehl liest Health und schickt die Werte hierher:</div>
      <ol class="steps small">
        <li>Kurzbefehle → Automation → Neu → <b>Tageszeit 21:30</b>, täglich, „Sofort ausführen“.</li>
        <li><b>VPN einschalten (für unterwegs):</b> <b>„Netzwerkdetails abrufen“</b> → <i>WLAN</i> / <i>Netzwerkname</i>. Dann <b>„Wenn“</b> <i>Netzwerkname</i> <b>ist nicht</b> <code>SkyNet</code>: <b>„VPN festlegen“ → Verbinden</b> (dein VPN wählen) und <b>„Warten“ 5 Sekunden</b>, damit der Tunnel wirklich steht. <b>Ende Wenn</b>.</li>
        <li>Aktion <b>„Health-Samples suchen“</b>: Typ <i>Aufgenommene Energie</i>, Startdatum <i>heute</i> → <b>„Statistiken berechnen“: Summe</b> → Variable <i>kcal</i>.</li>
        <li>Dasselbe für <i>Protein</i>, <i>Kohlenhydrate</i>, <i>Fett gesamt</i> (optional <i>Gewicht</i>: neuestes Sample).</li>
        <li>Aktion <b>„Inhalte von URL abrufen“</b>: URL <code>${esc(url)}</code>, Methode <b>POST</b>, Anfragetext <b>JSON</b> mit den Feldern <code>kcal</code>, <code>protein</code>, <code>carbs</code>, <code>fat</code> (und <code>weight</code>).</li>
        <li><b>Fehler melden:</b> <b>„Wenn“</b> <i>Inhalte von URL</i> <b>enthält nicht</b> <code>"ok":true</code>: <b>„Mitteilung zeigen“</b> „Yazio-Sync fehlgeschlagen“. <b>Ende Wenn</b>.</li>
        <li><b>VPN wieder aus:</b> <b>„Wenn“</b> <i>Netzwerkname</i> <b>ist nicht</b> <code>SkyNet</code>: <b>„VPN festlegen“ → Trennen</b>. <b>Ende Wenn</b>.</li>
      </ol>
      <div class="small muted">Im WLAN SkyNet bleibt das VPN aus. Der Import überschreibt den Tag – mehrfach senden ist ok.</div>
      <h3 style="margin-top:12px">Zweite Automation: gestern nachsenden (7:00)</h3>
      <div class="small">Fängt Tage auf, an denen um 21:30 nichts ankam (z. B. Training oder Spiel), und holt späte Snacks nach. Den Kurzbefehl oben duplizieren und so ändern:</div>
      <ol class="steps small">
        <li>Automation → Neu → <b>Tageszeit 7:00</b>, täglich, „Sofort ausführen“, mit dem duplizierten Kurzbefehl.</li>
        <li>Ganz oben: <b>„Datum“</b> (aktuelles Datum) → <b>„Datum anpassen“: Anfang von Tag</b> → Variable <i>heute0</i>. Dann <b>„Datum anpassen“: 1 Tag subtrahieren</b> von <i>heute0</i> → Variable <i>gestern0</i>.</li>
        <li>In jedem „Health-Samples suchen“ den Filter ändern auf <b>Startdatum ist zwischen <i>gestern0</i> und <i>heute0</i></b>.</li>
        <li><b>„Datum formatieren“</b>: <i>gestern0</i>, Format benutzerdefiniert <code>yyyy-MM-dd</code> → im JSON zusätzlich das Feld <code>date</code> damit füllen.</li>
      </ol>
      <div class="small muted">Ohne Feld <code>date</code> landet der Wert auf heute – dann wäre der Vortag falsch gebucht. Die Bezeichnungen können je nach iOS-Version leicht abweichen.</div></div>
    <div class="card"><h3>Für den Coach</h3><div class="small">Alle Einträge als JSON: <a href="/api/export" target="_blank">/api/export</a> – damit kann Claude (oder dein lokales LLM) den Plan anpassen.</div></div>`;
  $('#save').onclick = async () => {
    S.cfg.settings = await api('settings', { method: 'PUT', body: JSON.stringify({
      strength_days: +$('#sd').value, minutes: +$('#mi').value, level: $('#lv').value,
      kcal_target: +$('#kc').value, protein_target: +$('#pr').value, doctor_ok: $('#doc').checked }) });
    $('#saved').textContent = 'Gespeichert ✓';
  };
}

boot().catch(e => { view.innerHTML = `<div class="banner danger">Fehler beim Laden: ${esc(e.message)}</div>`; });
