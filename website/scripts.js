let currentChart = null;

// Function to create a chart container
function createChartContainer(id) {
  const container = document.createElement("div");
  container.className = "chart-container";
  const canvas = document.createElement("canvas");
  canvas.id = id;
  container.appendChild(canvas);
  return container;
}

// Function to create or update the chart
function updateChart(container, chartConfig) {
  // Destroy existing chart if it exists
  if (currentChart) {
    currentChart.destroy();
  }

  const ctx = container.querySelector("canvas").getContext("2d");

  // Parse the tooltip callback function from string if it exists
  if (chartConfig.options?.plugins?.tooltip?.callbacks?.label) {
    const labelFnStr = chartConfig.options.plugins.tooltip.callbacks.label;
    chartConfig.options.plugins.tooltip.callbacks.label = new Function(
      "return " + labelFnStr
    )();
  }

  currentChart = new Chart(ctx, chartConfig);
}

// Function to initialize the visualization
async function initializeVisualization() {
  try {
    // Fetch the chart data
    const response = await fetch("data/monthly_imports_by_continent.json");
    const chartData = await response.json();

    // Create container if it doesn't exist
    const chartsGrid = document.getElementById("charts-grid");
    chartsGrid.innerHTML = ""; // Clear existing content

    const container = createChartContainer("imports-chart");
    chartsGrid.appendChild(container);

    // Use the timeline view directly
    updateChart(container, chartData.timeline);
  } catch (error) {
    console.error("Error initializing visualization:", error);
  }
}

// Initialize when the document is ready
document.addEventListener("DOMContentLoaded", initializeVisualization);
