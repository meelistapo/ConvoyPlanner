const zerorpc = require("zerorpc");
const path = require('path');
let client = new zerorpc.Client();

connect();

function connect(){
    client.connect("tcp://127.0.0.1:4242");
    client.invoke("echo", "server ready", (error, res) => {
        if(error || res !== 'server ready') {
            console.error(error);
        } else {
            console.log("server is ready");
        }
    });

}

function getPaths(data, callback) {
        console.log(data);
        client.invoke("generatePaths", data, (error, result) => {
        if(error) {
            console.error(error);
            callback("error-"+error);
            createPyProc();
            connect();
        }
        else {
            console.log(result);
            callback(result);
        }
    })
}



let pyProc = null;
let pyPort = null;

const selectPort = () => {
    pyPort = 4242;
    return pyPort
};


function createPyProc() {
    let port = '' + selectPort();
    let script = path.join(__dirname, 'python', 'api.py');
    pyProc = require('child_process').spawn('python', [script, port]);
    if (pyProc != null) {
        console.log('child process success')
    }
}