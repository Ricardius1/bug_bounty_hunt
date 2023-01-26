const sio = io();

sio.on("connect", () => {
    console.log("Connected");
    // To receive data back from the server specify third argument (param) => {} that acts as a callback func
    sio.emit("sum", {numbers: [1, 2]}, (result) => {
        console.log(result);
    });
});


sio.on("disconnect", () => {
    console.log("Disconnected");
});


// Way to receive data on the client side
sio.on("sum_result", (data) => {
    console.log(data);
});


// To process an operation on the client side and send data back use this structure
// cb works here as a callback function
sio.on("mult", (data, cb) => {
    console.log(data);
    const result = data.numbers[0] * data.numbers[1];
    // result being sent back on the server where it was called from
    cb(result);
});


// Checks whether enter key was pressed and if True sends input.value on the server
let inputField = document.getElementById("inputField");

inputField.addEventListener("keyup", (event) => {
  if (event.key === "Enter") {
    sio.emit("message", inputField.value);
    inputField.value = "";
  }
});