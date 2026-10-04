const { app, BrowserWindow, Menu, shell } = require('electron');
const path = require('path');
function create() {
  const win = new BrowserWindow({
    width: 760, height: 900, minWidth: 360, minHeight: 560, title: 'Hanzi Arcade', icon: path.join(__dirname, '..', 'assets', 'icon.png'),
    autoHideMenuBar: true,
    webPreferences: { autoplayPolicy: 'no-user-gesture-required', contextIsolation: true, sandbox: true }
  });
  Menu.setApplicationMenu(null);
  win.loadFile(path.join(__dirname, '..', 'www', 'index.html'));
  win.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: 'deny' }; });
}
app.whenReady().then(create);
app.on('window-all-closed', () => app.quit());
