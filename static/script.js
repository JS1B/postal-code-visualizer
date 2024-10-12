function getDataPoints() {
    const table = document.getElementById('postcodes');
    const data = [];
    for (let i = 1; i < table.rows.length; i++) {
        row_data = [];
        for (let j = 0; j < table.rows[i].cells.length; j++) {
            row_data.push(table.rows[i].cells[j].innerText);
        }
        data.push(row_data);
    }
    return data;
}

async function fetchMapMetaData() {
    try {
        const response = await fetch('/map_meta');
        if (!response.ok) {
            throw new Error("HTTP error " + response.status);
        }
        mapMetaData = await response.json();
        return mapMetaData;
    } catch (error) {
        console.error("Error fetching meta data", error);
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

    return {"x": x, "y": y};
}

// Function to draw a circle at given coordinates
function drawCircle(canvas, ctx, lat, lon, referencePoints) {
    const points = fromCoordToPx(canvas, lat, lon, referencePoints);
    const r = 3;

    // Draw circle
    ctx.beginPath();
    ctx.arc(points.x, points.y, r, 0, Math.PI * 2, false);
    ctx.fillStyle = 'red';
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


function drawMapBackground(canvas, ctx, referencePoints) {
    const img = document.getElementById("mapImg");
    img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const data = getDataPoints();
        for (let i = 1; i < data.length; i++) {
            const coordinates = data[i][7].split('/');
            const lat = parseFloat(coordinates[0]);
            const lon = parseFloat(coordinates[1]);
            drawCircle(canvas, ctx, lat, lon, referencePoints);
            drawText(canvas, ctx, lat, lon, referencePoints, data[i][1]);
        }
        canvas.style.display = 'block';
    };
    img.onload();
}

async function drawMap() {
    // Set up canvas
    const canvas = document.getElementById('mapCanvas');
    const ctx = canvas.getContext('2d');
    ctx.font = "10px Arial"

    drawStaticBackground(canvas, ctx);
    const referencePoints = await fetchMapMetaData();

    drawMapBackground(canvas, ctx, referencePoints);
}

document.addEventListener('DOMContentLoaded', drawMap);