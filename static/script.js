async function getData() {
    try {
        const response = await fetch('/data'); // Fetch data from the server
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json(); // Parse the JSON response
        return data; // Return the data
    } catch (error) {
        console.error("Error fetching data:", error);
        return []; // Return an empty array in case of an error
    }
}

async function fetchMapMetaData() {
    try {
        const response = await fetch('/map_meta');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching map metadata:", error);
        return {};
    }
}

function fromCoordToPx(canvas, lat, lon, referencePoints) {
    const img = document.getElementById("mapImg");
    const scaling_factor_X = img.width / canvas.width; // I assume Y is the same
    console.assert(scaling_factor_X === img.height / canvas.height, "Scaling factors are not equal");

    let x = (lon - referencePoints.wizajny.lon) / (referencePoints.bystrzyca.lon - referencePoints.wizajny.lon) * (referencePoints.bystrzyca.x - referencePoints.wizajny.x) + referencePoints.wizajny.x;
    x /= scaling_factor_X;
    let y = (lat - referencePoints.wizajny.lat) / (referencePoints.bystrzyca.lat - referencePoints.wizajny.lat) * (referencePoints.bystrzyca.y - referencePoints.wizajny.y) + referencePoints.wizajny.y;
    y /= scaling_factor_X;

    return { "x": x, "y": y };
}

// Function to draw a circle at given coordinates
function drawCircle(canvas, ctx, lat, lon, referencePoints, color) {
    const points = fromCoordToPx(canvas, lat, lon, referencePoints);
    const r = 1;

    // Draw circle
    ctx.beginPath();
    ctx.arc(points.x, points.y, r, 0, Math.PI * 2, false);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.closePath();
}

function drawText(canvas, ctx, lat, lon, referencePoints, text) {
    const points = fromCoordToPx(canvas, lat, lon, referencePoints);
    ctx.fillText(text, points.x, points.y);
}

function drawStaticBackground(canvas, ctx) {
    ctx.fillStyle = 'grey';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawMapBackground(canvas, ctx) {
    const img = document.getElementById("mapImg");
    img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        canvas.style.display = 'block';
    };
    img.onload();
}

function drawMapCircles(canvas, ctx, dataPoints, referencePoints, color) {
    for (const dataPoint of dataPoints) {
        const coordinates = dataPoint[7].split('/');
        const lat = parseFloat(coordinates[0]);
        const lon = parseFloat(coordinates[1]);
        drawCircle(canvas, ctx, lat, lon, referencePoints, color);
        // drawText(canvas, ctx, lat, lon, referencePoints, dataPoint[1], color);
    }
}

async function drawMap() {
    // Set up canvas
    const canvas = document.getElementById('mapCanvas');
    const ctx = canvas.getContext('2d');
    ctx.font = "10px Arial"

    drawStaticBackground(canvas, ctx);
    const referencePoints = await fetchMapMetaData();
    const data = await getData();
    const dataPoints = data.all;
    const top2Points = data.top2.flatMap((place) => {
        const placeName = place[0][0];
        const admin1 = place[0][1];
        const admin2 = place[0][2];
        const admin3 = place[0][3];
      
        return data.all.filter(point =>
          point[1] === placeName &&
          point[4] === admin1 &&
          point[5] === admin2 &&
          point[6] === admin3
        );
    });
    drawMapBackground(canvas, ctx);
    drawMapCircles(canvas, ctx, dataPoints, referencePoints, 'red');
    drawMapCircles(canvas, ctx, top2Points, referencePoints, 'white');

    // BS
    const boundingBox = getBoundingBox(top2Points);
    drawBoundingBox(ctx, boundingBox);
    const sectors = divideIntoSectors(boundingBox);
    
    // Draw density map and count postal codes in each sector
    const sectorCounts = countPostalCodesInSectors(top2Points, sectors);
    drawDensityMap(canvas, ctx, sectors, sectorCounts);
}

function getBoundingBox(dataPoints) {
    return {}
}

function drawBoundingBox(ctx, boundingBox) {
    ctx.beginPath();
    ctx.rect(boundingBox.x, boundingBox.y, boundingBox.width, boundingBox.height);
    ctx.stroke();
}

function divideIntoSectors(boundingBox) {
    const sectors = [];
    const sectorWidth = boundingBox.width / 3;
    const sectorHeight = boundingBox.height / 3;
    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            sectors.push({
                x: boundingBox.x + i * sectorWidth,
                y: boundingBox.y + j * sectorHeight,
                width: sectorWidth,
                height: sectorHeight
            });
        }
    }
    return sectors;
}

function countPostalCodesInSectors(dataPoints, sectors) {

}

function drawDensityMap(canvas, ctx, sectors, sectorCounts) {

}

document.addEventListener('DOMContentLoaded', drawMap);