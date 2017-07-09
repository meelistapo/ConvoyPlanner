const zerorpc = require("zerorpc");
let client = new zerorpc.Client();

client.connect("tcp://127.0.0.1:4242");
client.invoke("echo", "server ready", (error, res) => {
    if(error || res !== 'server ready') {
        console.error(error);
    } else {
        console.log("server is ready");
    }
});

// let formula = document.querySelector('#formula');
// let result = document.querySelector('#result');


function getPaths(data, callback) {
        console.log(data)
        client.invoke("generatePaths", data, (error, result) => {
        if(error) {
            console.error(error);
        }
        else {
            console.log(result);
            callback(result.textContent);
        }
    })
}
// formula.addEventListener('input', () => {
//     client.invoke("calc", formula.value, (error, res) => {
//         if(error) {
//             console.error(error);
//         } else {
//             result.textContent = res;
//         }
//     })
// });
//
// formula.dispatchEvent(new Event('input'));




// client.invoke("calc", "hei", (error, res) => {
//     console.log("siin");
//     if(error) {
//         console.error("error");
//         console.error(error)
//     } else {
//         result.textContent = res
//     }
// });

