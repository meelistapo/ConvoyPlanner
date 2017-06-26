const {app, BrowserWindow} = require('electron');
const path = require('path');
require('electron-debug')({showDevTools: true});

// int win
let win;

let pyProc = null;
let pyPort = null;

const selectPort = () => {
    pyPort = 4242;
    return pyPort
};

const createPyProc = () => {
    let port = '' + selectPort();
    let script = path.join(__dirname, 'python', 'api.py');
    pyProc = require('child_process').spawn('python', [script, port]);
    if (pyProc != null) {
        console.log('child process success')
    }
};

const exitPyProc = () => {
    pyProc.kill();
    pyProc = null;
    pyPort = null;
};

// run createWindow function
app.on('ready', createWindow);

app.on('ready', createPyProc);
app.on('will-quit', exitPyProc);

// quit when all windows are closed
app.on('window-all-closed', () => {
    if(process.platform !== 'darwin'){
        app.quit();
    }
});

// create browser window
function createWindow(){
    win = new BrowserWindow({width:1200, height: 800});

    // load index.html
    win.loadURL(`file://${__dirname}/index.html`);

    win.on('closed', () =>{
        win = null;
    });
}