const zoomIncrement = -0.002;
const rotateIncrement = 0.2;
const latIncrement = 0.000005;
const frameInterval = 1000;
let frameCounter = 1;
let isAnimating = false;
let intervalId = null;
let selectedActionIndex = null; // Stores the randomly chosen action (0, 1, or 2)

// Define the action to perform (based on selectedActionIndex)
function performAction() {
    switch (selectedActionIndex) {
        case 0: // Rotate
            const currentBearing = map.getBearing();
            map.rotateTo(currentBearing + rotateIncrement, { duration: 0 });
            break;
        case 1: // Zoom
            const currentZoom = map.getZoom();
            map.setZoom(currentZoom + zoomIncrement, { duration: 0 });
            break;
        case 2: // Pan
            const currentCenter = map.getCenter();
            map.setCenter([currentCenter.lng, currentCenter.lat + latIncrement], { duration: 0 });
            break;
    }
}

// Capture a frame after the action completes
function animateFrame() {
    if (isAnimating) return;
    isAnimating = true;

    performAction(); // Execute the pre-selected action

    map.once('idle', () => {
        const canvas = map.getCanvas();
        const paddedFrameCounter = String(frameCounter).padStart(4, '0');
        canvas.toBlob(function (blob) {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `frame_${paddedFrameCounter}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            frameCounter++;
            isAnimating = false;
        }, 'image/png');
    });
}

// Toggle animation on button click
const actionOverlay = document.getElementById('actionOverlay');
if (actionOverlay) {
    actionOverlay.addEventListener('click', () => {
        if (intervalId) {
            // Stop animation
            clearInterval(intervalId);
            intervalId = null;
            selectedActionIndex = null; // Reset action
            frameCounter = 1;
            console.log("Animation stopped");
        } else {
            // Start animation (pick a random action ONCE)
            selectedActionIndex = Math.floor(Math.random() * 3); // 0=rotate, 1=zoom, 2=pan
            intervalId = setInterval(animateFrame, frameInterval);
            console.log(`Animation started with action: ${selectedActionIndex}`);
        }
    });
}

map.on('click', (e) => {
    const features = map.queryRenderedFeatures(e.point);
    if (features.length > 0) {
        console.log('Clicked feature:', features[0].properties);
    } else {
        console.log('No features at this location');
    }
});