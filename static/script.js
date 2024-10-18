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
    const r = .6;

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
    const top2Points = data.top2.map((place) => {
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
    drawMapCircles(canvas, ctx, top2Points[0], referencePoints, 'lightblue');
    drawMapCircles(canvas, ctx, top2Points[1], referencePoints, 'blue');

    // BS
    const boundingBox = [getBoundingBox(canvas, referencePoints, top2Points[0]), getBoundingBox(canvas, referencePoints, top2Points[1])];
    drawBoundingBox(ctx, boundingBox[0]);
    drawBoundingBox(ctx, boundingBox[1]);
    const sectors = [divideIntoSectors(boundingBox[0]), divideIntoSectors(boundingBox[1])];
    
    // Draw density map and count postal codes in each sector
    const sectorCounts = [countPostalCodesInSectors(canvas, top2Points[0], sectors[0], referencePoints), countPostalCodesInSectors(canvas, top2Points[1], sectors[1], referencePoints)];
    drawDensityMap(canvas, ctx, sectors[0], sectorCounts[0]);
    drawDensityMap(canvas, ctx, sectors[1], sectorCounts[1]);
}

function getBoundingBox(canvas, referencePoints, dataPoints) {
    let minLon = Number.MAX_VALUE;
    let minLat = Number.MAX_VALUE;
    let maxLon = Number.MIN_VALUE;
    let maxLat = Number.MIN_VALUE;
    for (const dataPoint of dataPoints) {
        const coordinates = dataPoint[7].split('/');
        const lat = parseFloat(coordinates[0]);
        const lon = parseFloat(coordinates[1]);
        minLon = Math.min(minLon, lon);
        minLat = Math.min(minLat, lat);
        maxLon = Math.max(maxLon, lon);
        maxLat = Math.max(maxLat, lat);
    }
    const lower_position = fromCoordToPx(canvas, maxLat, minLon, referencePoints);
    const upper_position = fromCoordToPx(canvas, minLat, maxLon, referencePoints);
    return {
        x: lower_position.x,
        y: lower_position.y,
        width: upper_position.x - lower_position.x,
        height: upper_position.y - lower_position.y
    };
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

function countPostalCodesInSectors(canvas, dataPoints, sectors, referencePoints) {
    const sectorCounts = [];
    for (let i = 0; i < sectors.length; i++) {
        sectorCounts.push(0);
    }
    for (const dataPoint of dataPoints) {
        const coordinates = dataPoint[7].split('/');
        const lat = parseFloat(coordinates[0]);
        const lon = parseFloat(coordinates[1]);
        const position_on_map = fromCoordToPx(canvas, lat, lon, referencePoints);

        for (let i = 0; i < sectors.length; i++) {
            // console.log(position_on_map, sectors[i]);
            if (position_on_map.x >= sectors[i].x && position_on_map.x < sectors[i].x + sectors[i].width &&
                position_on_map.y >= sectors[i].y && position_on_map.y < sectors[i].y + sectors[i].height) {
                sectorCounts[i]++;
                break;
            }
        }
    }
    return sectorCounts;
}

function drawDensityMap(canvas, ctx, sectors, sectorCounts) {
    const maxCount = sectorCounts.reduce((partialSum, a) => partialSum + a, 0); // Or use Math.max(...sectorCounts)
    for (let i = 0; i < sectors.length; i++) {
        const sector = sectors[i];
        const count = sectorCounts[i];
        const color = `rgba(0, 255, 0, ${count / maxCount})`;
        ctx.fillStyle = color;
        ctx.fillRect(sector.x, sector.y, sector.width, sector.height);
    }
}

document.addEventListener('DOMContentLoaded', drawMap);