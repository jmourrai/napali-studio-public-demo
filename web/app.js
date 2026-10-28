/* Standalone public demo; all displayed records are synthetic. No client telemetry. */
const stages = [
  ['intake', 'Intake'], ['review', 'Review'], ['in_progress', 'In progress'],
  ['approval', 'Approval'], ['published', 'Published'],
];
let items = [];
let transitions = {};

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text; // Avoid interpreting API data as HTML.
  return node;
}

function notice(text, error = false) {
  const node = document.getElementById('notice');
  node.textContent = text;
  node.hidden = false;
  node.classList.toggle('error', error);
}

async function api(path, options = {}) {
  const response = await fetch(path, {headers: {'Content-Type': 'application/json'}, ...options});
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const msg = typeof data.detail === 'string' ? data.detail : `Request failed (${response.status})`;
    throw new Error(msg);
  }
  return response.json();
}

function render(items, stats) {
  document.getElementById('stat-total').textContent = stats.total;
  document.getElementById('stat-progress').textContent = stats.by_status.in_progress;
  document.getElementById('stat-approval').textContent = stats.by_status.approval;
  document.getElementById('stat-published').textContent = stats.by_status.published;
  const board = document.getElementById('columns');
  board.replaceChildren();
  for (const [status, title] of stages) {
    const lane = el('div', 'lane');
    const header = el('div', 'lane-header');
    header.append(el('span', 'lane-title', title));
    const matching = items.filter(item => item.status === status);
    header.append(el('span', 'count', String(matching.length)));
    lane.append(header);
    if (!matching.length) lane.append(el('p', 'lane-empty', 'Nothing here yet'));
    for (const item of matching) {
      const card = el('article', 'work-card');
      card.append(el('div', 'card-id', `ITEM ${item.id.slice(0, 6).toUpperCase()} · v${item.version}`));
      card.append(el('h3', '', item.title));
      card.append(el('p', '', item.description || 'No details provided'));
      const bottom = el('div', 'card-bottom');
      bottom.append(el('span', `pill ${item.priority}`, item.priority));
      const actions = el('div', 'card-actions');
      const inspect = el('button', 'ghost', 'History');
      inspect.type = 'button';
      inspect.addEventListener('click', () => showDetail(item));
      actions.append(inspect);
      const next = transitions[item.status] || [];
      if (next.length) {
        const primary = next.find(s => stages.findIndex(stage => stage[0] === s) > stages.findIndex(stage => stage[0] === item.status)) || next[0];
        const advance = el('button', 'advance', primary === 'published' ? 'Publish →' : 'Next →');
        advance.type = 'button';
        advance.title = `Move to ${primary.replace('_', ' ')}`;
        advance.addEventListener('click', () => moveItem(item, primary));
        actions.append(advance);
      }
      bottom.append(actions); card.append(bottom); lane.append(card);
    }
    board.append(lane);
  }
}

async function refresh() {
  try {
    [items, transitions] = await Promise.all([
      api('/api/work-items'),
      api('/api/workflow').then(data => data.allowed_transitions),
    ]);
    const stats = await api('/api/metrics');
    render(items, stats);
  } catch (error) { notice(error.message, true); }
}

async function moveItem(item, state) {
  try {
    await api(`/api/work-items/${item.id}/transition`, {
      method: 'POST',
      body: JSON.stringify({to_status: state, expected_version: item.version,
                            note: 'Advanced from the public demo board'}),
    });
    notice(`Moved “${item.title}” to ${state.replace('_', ' ')}.`);
  } catch (error) { notice(`${error.message}. Reloading the board.`, true); }
  await refresh();
}

async function showDetail(item) {
  document.getElementById('detail-title').textContent = item.title;
  document.getElementById('detail-description').textContent = item.description || 'No description';
  document.getElementById('detail-metadata').textContent = `Status: ${item.status.replace('_',' ')}  ·  Priority: ${item.priority}  ·  Version: ${item.version}`;
  const list = document.getElementById('audit-events');
  list.textContent = 'Loading…';
  document.getElementById('detail-dialog').showModal();
  try {
    const events = await api(`/api/work-items/${item.id}/events`);
    list.replaceChildren();
    for (const event of events) {
      const line = el('div', 'audit-event');
      line.append(el('b', '', `${event.from_status || 'New'} → ${event.to_status}`));
      line.append(el('div', '', event.note || 'No note'));
      line.append(el('small', '', `${event.created_at} UTC · ${event.actor}`));
      list.append(line);
    }
  } catch (error) { list.textContent = error.message; }
}

async function createItem(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const data = Object.fromEntries(new FormData(form));
  try {
    await api('/api/work-items', {method: 'POST', body: JSON.stringify(data)});
    document.getElementById('create-dialog').close();
    form.reset();
    notice('Created a new synthetic work item.');
    await refresh();
  } catch (error) { notice(error.message, true); }
}

document.getElementById('create-open').addEventListener('click', () => document.getElementById('create-dialog').showModal());
document.getElementById('create-form').addEventListener('submit', createItem);
document.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => document.getElementById(button.dataset.close).close()));
refresh();
