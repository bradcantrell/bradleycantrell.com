/**
 * Conway's Game of Life — GMUNK aesthetic (Oblivion interface inspired)
 * Dark aesthetic with pink (#FF64C8) and cyan (#64D8FF) accents
 * Wireframe geometry with chromatic aberration and glitch effects
 * 
 * Aesthetic principles:
 * - Deep black background with neon pink/cyan wireframe grids
 * - Chromatic separation (RGB shift) with Oblivion color palette
 * - Random glitches and artifacts
 * - The cellular automaton as surveillance, as pattern, as haunting presence
 */

let grid;
let cols, rows;
let cellSize = 6;
let time = 0;
let glitchIntensity = 0.03;
let chromaticAberration = 4;
let pink, cyan, black;

function setup() {
  let canvas = createCanvas(windowWidth, windowHeight);
  canvas.parent('gol-canvas-container');
  
  colorMode(HSB, 360, 100, 100, 1);
  
  pink = color(180, 120, 80);   // warm copper
  cyan = color(200, 184, 154);  // warm gold (matches site --accent)
  black = color(0, 0, 0);
  
  // Ensure black background
  background(0);
  
  // Initialize grid
  cols = floor(width / cellSize);
  rows = floor(height / cellSize);
  grid = makeGrid();
  
  // Initial random state
  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      grid[i][j] = random() > 0.85 ? 1 : 0;
    }
  }
  
  loop();
}

function makeGrid() {
  let g = [];
  for (let i = 0; i < cols; i++) {
    g[i] = [];
    for (let j = 0; j < rows; j++) {
      g[i][j] = 0;
    }
  }
  return g;
}

function draw() {
  // Fade effect for trail
  noStroke();
  fill(0, 0, 0, 10);
  rect(0, 0, width, height);
  
  time += 0.02;
  
  // Apply glitches randomly
  if (random() < glitchIntensity) {
    applyGlitch();
  }
  
  // Draw cells with chromatic aberration
  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      if (grid[i][j] === 1) {
        let x = i * cellSize;
        let y = j * cellSize;
        
        // RGB split with Oblivion colors
        drawCellWithAberration(x, y, -chromaticAberration, color(200, 184, 154)); // Gold offset
        drawCellWithAberration(x, y, chromaticAberration, color(180, 120, 80));   // Copper offset
        drawCell(x, y, 0); // Cyan center
        
        // Wireframe grid lines for live cells
        stroke(35, 60, 55, 30);  // warm amber wireframe
        strokeWeight(0.5);
        noFill();
        rect(x, y, cellSize, cellSize);
      }
    }
  }
  
  // Update grid
  let nextGrid = makeGrid();
  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      let neighbors = countNeighbors(i, j);
      if (grid[i][j] === 1) {
        if (neighbors === 2 || neighbors === 3) {
          nextGrid[i][j] = 1;
        }
      } else {
        if (neighbors === 3) {
          nextGrid[i][j] = 1;
        }
      }
    }
  }
  grid = nextGrid;
}

function drawCell(x, y, hueShift) {
  let hue = (hueShift + 180) % 360;
  stroke(hue, 90, 100, 80);
  strokeWeight(2);
  point(x + cellSize/2, y + cellSize/2);
}

function drawCellWithAberration(x, y, offset, col) {
  let colHue = hue(col);
  stroke(colHue, 85, 95, 60);
  strokeWeight(1.5);
  point(x + cellSize/2 + offset, y + cellSize/2);
}

function countNeighbors(x, y) {
  let sum = 0;
  for (let i = -1; i <= 1; i++) {
    for (let j = -1; j <= 1; j++) {
      let col = (x + i + cols) % cols;
      let row = (y + j + rows) % rows;
      sum += grid[col][row];
    }
  }
  sum -= grid[x][y];
  return sum;
}

function applyGlitch() {
  let glitchWidth = floor(random(10, 50));
  let glitchHeight = floor(random(20, 100));
  let glitchX = floor(random(width - glitchWidth));
  let glitchY = floor(random(height - glitchHeight));
  
  // Shift a slice of pixels
  let slice = get(glitchX, glitchY, glitchWidth, glitchHeight);
  let offset = floor(random(-10, 10));
  image(slice, glitchX + offset, glitchY);
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
  cols = floor(width / cellSize);
  rows = floor(height / cellSize);
  grid = makeGrid();
  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      grid[i][j] = random() > 0.85 ? 1 : 0;
    }
  }
}
