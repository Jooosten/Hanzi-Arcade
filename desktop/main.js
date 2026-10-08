const { app, BrowserWindow, Menu, shell } = require('electron');
const path = require('path');
/* Auto-fit: on a big window everything scales up (like browser zoom) so text is larger and the app fills the screen.
   Windows up to about 1180x760 stay at 100%; a maximised 1920x1080 screen lands around 135-140%. */
function fitZoom(win) {
  if (win.isDestroyed()) return;
  const [w, h] = win.getContentSize();
  const z = Math.max(1, Math.min(2, Math.min(w / 1180, h / 760)));
  win.webContents.setZoomFactor(Math.round(z * 20) / 20);
}

function create() {
  const win = new BrowserWindow({
    width: 1280, height: 720, useContentSize: true, minWidth: 360, minHeight: 560, title: 'Hanzi Arcade', icon: path.join(__dirname, '..', 'assets', 'icon.png'),
    autoHideMenuBar: true,
    webPreferences: { autoplayPolicy: 'no-user-gesture-required', contextIsolation: true, sandbox: true }
  });
  Menu.setApplicationMenu(null);
  win.webContents.on('did-finish-load', () => fitZoom(win));
  win.on('resize', () => fitZoom(win));
  win.loadFile(path.join(__dirname, '..', 'www', 'index.html'));
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: 'deny' }; });
}
app.whenReady().then(create);
app.on('window-all-closed', () => app.quit());
