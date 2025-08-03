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

// Function to update the year selector
function updateYearSelector(years, onYearChange) {
  const yearSelect = document.getElementById("yearSelect");
  yearSelect.innerHTML = ""; // Clear existing options

  years.forEach((year) => {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    yearSelect.appendChild(option);
  });

  // Set initial year to the most recent one
  yearSelect.value = years[years.length - 1];

  // Add change event listener
  yearSelect.addEventListener("change", (e) => {
    onYearChange(e.target.value);
  });
}

// Function to create or update the chart
function updateChart(container, yearData) {
  // Destroy existing chart if it exists
  if (currentChart) {
    currentChart.destroy();
  }

  const ctx = container.querySelector("canvas").getContext("2d");
  currentChart = new Chart(ctx, {
    type: yearData.type,
    data: yearData.data,
    options: {
      ...yearData.options,
      responsive: true,
      maintainAspectRatio: false,
    },
  });

  // Update description
  let descriptionEl = container.querySelector(".chart-description");
  if (!descriptionEl) {
    descriptionEl = document.createElement("p");
    descriptionEl.className = "chart-description";
    container.appendChild(descriptionEl);
  }
  descriptionEl.textContent = yearData.description;
}

// Function to initialize the visualization
async function initializeVisualization() {
  try {
    // Fetch the chart data
    const response = await fetch("data/monthly_imports_by_continent.json");
    const chartData = await response.json();

    // Get sorted years
    const years = Object.keys(chartData).sort();

    // Create container if it doesn't exist
    const chartsGrid = document.getElementById("charts-grid");
    chartsGrid.innerHTML = ""; // Clear existing content

    const container = createChartContainer("imports-chart");
    chartsGrid.appendChild(container);

    // Initialize year selector
    updateYearSelector(years, (selectedYear) => {
      updateChart(container, chartData[selectedYear]);
    });

    // Show initial chart with the most recent year
    updateChart(container, chartData[years[years.length - 1]]);
  } catch (error) {
    console.error("Error initializing visualization:", error);
  }
}

// Initialize when the document is ready
document.addEventListener("DOMContentLoaded", initializeVisualization);
