const { app, BrowserWindow, Menu, shell } = require('electron');
const path = require('path');
const fs = require('fs');

/* Zoom: Ctrl + / Ctrl - / Ctrl 0, or Ctrl + mouse wheel. The level is remembered between launches. */
const ZOOM_MIN = 0.5, ZOOM_MAX = 3, ZOOM_STEP = 0.1;
const zoomFile = () => path.join(app.getPath('userData'), 'zoom.json');
const clampZoom = z => Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, Math.round(z * 10) / 10));
function loadZoom() {
  try { const z = Number(JSON.parse(fs.readFileSync(zoomFile(), 'utf8')).zoom); return Number.isFinite(z) ? clampZoom(z) : 1; } catch (e) { return 1; }
}
function saveZoom(z) { try { fs.writeFileSync(zoomFile(), JSON.stringify({ zoom: z })); } catch (e) { /* not worth failing over */ } }

function create() {
  const win = new BrowserWindow({
    width: 760, height: 900, minWidth: 360, minHeight: 560, title: 'Hanzi Arcade', icon: path.join(__dirname, '..', 'assets', 'icon.png'),
    autoHideMenuBar: true,
    webPreferences: { autoplayPolicy: 'no-user-gesture-required', contextIsolation: true, sandbox: true }
  });
  Menu.setApplicationMenu(null);
  const wc = win.webContents;
  let zoom = loadZoom();
  const setZoom = z => { zoom = clampZoom(z); wc.setZoomFactor(zoom); saveZoom(zoom); };
  wc.on('did-finish-load', () => wc.setZoomFactor(zoom));
  wc.on('before-input-event', (e, input) => {
    if (input.type !== 'keyDown' || !(input.control || input.meta) || input.alt) return;
    const k = input.key;
    if (k === '=' || k === '+' || k === 'Add') { setZoom(zoom + ZOOM_STEP); e.preventDefault(); }
    else if (k === '-' || k === '_' || k === 'Subtract') { setZoom(zoom - ZOOM_STEP); e.preventDefault(); }
    else if (k === '0') { setZoom(1); e.preventDefault(); }
  });
  wc.on('zoom-changed', (e, direction) => setZoom(zoom + (direction === 'in' ? ZOOM_STEP : -ZOOM_STEP)));
  win.loadFile(path.join(__dirname, '..', 'www', 'index.html'));
  wc.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: 'deny' }; });
}
app.whenReady().then(create);
app.on('window-all-closed', () => app.quit());
