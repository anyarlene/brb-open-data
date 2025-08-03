let currentChart = null;
let chartData = null;

// Function to create or update the chart
function updateChart(year) {
  // Destroy existing chart if it exists
  if (currentChart) {
    currentChart.destroy();
  }

  const ctx = document.getElementById("importChart").getContext("2d");
  const yearData = chartData.data[year];

  const config = {
    type: chartData.type,
    data: yearData,
    options: chartData.options,
  };

  // Parse the tooltip callback function from string if it exists
  if (config.options?.plugins?.tooltip?.callbacks?.label) {
    const labelFnStr = config.options.plugins.tooltip.callbacks.label;
    config.options.plugins.tooltip.callbacks.label = new Function(
      "return " + labelFnStr
    )();
  }

  // Update the chart title with the selected year
  config.options.plugins.title.text = `${chartData.title} - ${year}`;

  currentChart = new Chart(ctx, config);
}

// Function to populate year select dropdown
function populateYearSelect(years) {
  const yearSelect = document.getElementById("yearSelect");
  yearSelect.innerHTML = ""; // Clear existing options

  years.forEach((year) => {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    yearSelect.appendChild(option);
  });

  // Select the most recent year by default
  yearSelect.value = years[years.length - 1];
}

// Function to initialize the visualization
async function initializeVisualization() {
  try {
    // Fetch the chart data
    const response = await fetch("data/monthly_imports_by_continent.json");
    chartData = await response.json();

    // Populate year select dropdown
    populateYearSelect(chartData.years);

    // Add event listener for year selection
    const yearSelect = document.getElementById("yearSelect");
    yearSelect.addEventListener("change", (e) => updateChart(e.target.value));

    // Initialize chart with the most recent year
    updateChart(chartData.years[chartData.years.length - 1]);
  } catch (error) {
    console.error("Error initializing visualization:", error);
  }
}

// Initialize when the document is ready
document.addEventListener("DOMContentLoaded", initializeVisualization);
