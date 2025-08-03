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

// Function to set up the year slider
function setupYearSlider(years) {
  const yearSlider = document.getElementById("yearSlider");
  const selectedYearSpan = document.getElementById("selectedYear");

  // Configure slider
  yearSlider.min = 0;
  yearSlider.max = years.length - 1;
  yearSlider.value = years.length - 1; // Start with most recent year
  yearSlider.step = 1;

  // Update selected year display
  selectedYearSpan.textContent = years[yearSlider.value];

  // Add event listeners
  yearSlider.addEventListener("input", (e) => {
    const selectedYear = years[e.target.value];
    selectedYearSpan.textContent = selectedYear;
    updateChart(selectedYear);
  });

  return years[yearSlider.value]; // Return initial year
}

// Function to initialize the visualization
async function initializeVisualization() {
  try {
    // Fetch the chart data
    const response = await fetch("data/monthly_imports_by_continent.json");
    chartData = await response.json();

    // Set up year slider and get initial year
    const initialYear = setupYearSlider(chartData.years);

    // Initialize chart with the initial year
    updateChart(initialYear);
  } catch (error) {
    console.error("Error initializing visualization:", error);
  }
}

// Initialize when the document is ready
document.addEventListener("DOMContentLoaded", initializeVisualization);
