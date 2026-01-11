const pubnub = new PubNub({
  publishKey: window.PUBNUB_CONFIG.publishKey,
  subscribeKey: window.PUBNUB_CONFIG.subscribeKey,
  uuid: "web-client"
});

const channel = "motion_channel";

pubnub.addListener({
    message: function (event) {
        if (event.message.motion) {
            document.getElementById("status").innerText =
                "🚨 Motion detected!";
        }
    }
});

pubnub.subscribe({
    channels: [channel]
});
