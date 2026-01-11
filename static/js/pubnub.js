// Initialize PubNub
let pubnub = null;

// Function to initialize PubNub based on motion detection setting
function initializePubNub() {
    if (!window.PUBNUB_CONFIG || !window.PUBNUB_CONFIG.publishKey || !window.PUBNUB_CONFIG.subscribeKey) {
        console.error('PubNub configuration missing');
        return;
    }
    
    pubnub = new PubNub({
        publishKey: window.PUBNUB_CONFIG.publishKey,
        subscribeKey: window.PUBNUB_CONFIG.subscribeKey,
        uuid: "user-" + Math.random().toString(36).substr(2, 9),
        restore: true,
        heartbeatInterval: 60
    });
    
    // Only subscribe if motion detection is enabled
    if (window.USER_CONFIG && window.USER_CONFIG.motionEnabled) {
        setupPubNubListener();
    }
    
    // Store for global access
    window.pubnubClient = pubnub;
}

// Setup PubNub listener
function setupPubNubListener() {
    if (!pubnub) return;
    
    pubnub.addListener({
        status: function(statusEvent) {
            if (statusEvent.category === "PNConnectedCategory") {
                console.log("Connected to motion detection system");
                addActivityLog("Connected to motion detection", "Just now");
            } else if (statusEvent.category === "PNReconnectedCategory") {
                console.log("Reconnected to motion detection system");
            } else if (statusEvent.category === "PNNetworkDownCategory") {
                console.log("Network connection lost");
            }
        },
        
        message: function(event) {
            console.log("Motion event received:", event.message);
            
            if (event.message.motion === true || event.message.motion === "detected") {
                showMotionAlert(event.message);
                addActivityLog("Motion detected!", new Date().toLocaleTimeString());
            }
        },
        
        presence: function(presenceEvent) {
            console.log("Presence event:", presenceEvent);
        }
    });

    // Subscribe to channel
    pubnub.subscribe({
        channels: ['motion_channel'],
        withPresence: true,
        withPresenceTimeout: 120
    });
}

// Toggle PubNub subscription based on motion detection setting
function togglePubNubSubscription(enabled) {
    if (!pubnub) return;
    
    if (enabled) {
        setupPubNubListener();
        console.log('Motion detection enabled - Subscribed to PubNub');
    } else {
        pubnub.unsubscribe({
            channels: ['motion_channel']
        });
        console.log('Motion detection disabled - Unsubscribed from PubNub');
    }
}

// Show motion alert
function showMotionAlert(message) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = 'alert-notification';
    alert.innerHTML = `
        <div class="alert-content">
            <div class="alert-icon">🚨</div>
            <div class="alert-text">
                <div class="alert-title">Motion Detected!</div>
                <div class="alert-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</div>
            </div>
        </div>
    `;
    
    document.body.appendChild(alert);
    
    // Play alert sound
    playAlertSound();
    
    // Remove alert after 5 seconds
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

// Play alert sound
function playAlertSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.8);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.8);
    } catch (e) {
        console.log('Audio not supported or user blocked it');
    }
}

// Add activity to log
function addActivityLog(title, time) {
    const activityList = document.getElementById('activity-list');
    if (activityList) {
        const activityItem = document.createElement('li');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <div class="activity-icon">
                <i class="fas fa-bell"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${title}</div>
                <div class="activity-time">${time}</div>
            </div>
        `;
        activityList.insertBefore(activityItem, activityList.firstChild);
        
        // Limit to 10 items
        if (activityList.children.length > 10) {
            activityList.removeChild(activityList.lastChild);
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializePubNub();
    
    // Request notification permission
    if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission().then(permission => {
            console.log("Notification permission:", permission);
        });
    }
});

// Export functions for global use
window.togglePubNubSubscription = togglePubNubSubscription;
window.showMotionAlert = showMotionAlert;