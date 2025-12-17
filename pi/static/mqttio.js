let client = null;

function connect() {
    let ip = location.hostname;
    client = new Paho.MQTT.Client(ip, 9001, "web-" + parseInt(Math.random() * 10000));
    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;
    client.connect({ onSuccess: onConnect });
}

function onConnect() {
    console.log("MQTT Connected");
    client.subscribe("santa/photo"); 
}

function onConnectionLost(res) {
    if (res.errorCode !== 0) console.log("연결 끊김: " + res.errorMessage);
}

function onMessageArrived(msg) {
    if(msg.destinationName == "santa/photo") {
        let filename = msg.payloadString;
        let img = document.getElementById("santa-photo");
        let txt = document.getElementById("photo-msg");
        
        img.src = "./static/" + filename;
        img.style.display = "block";
        txt.innerText = "⚠️ 침입자 감지! (" + new Date().toLocaleTimeString() + ")";
        alert("🎅 산타가 감지되었습니다!");
    }
}

function publish(topic, msg) {
    let message = new Paho.MQTT.Message(String(msg));
    message.destinationName = topic;
    client.send(message);
}
