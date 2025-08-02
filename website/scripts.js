// Function to create a chart container
function createChartContainer(id) {
  const container = document.createElement("div");
  container.className = "chart-container";
  const canvas = document.createElement("canvas");
  canvas.id = id;
  container.appendChild(canvas);
  return container;
}

// Function to create a chart
async function createChart(jsonFile) {
  try {
    const response = await fetch(`data/${jsonFile}`);
    const chartData = await response.json();

    const chartId = jsonFile.replace(".json", "");
    const container = createChartContainer(chartId);
    document.getElementById("charts-grid").appendChild(container);

    const ctx = document.getElementById(chartId).getContext("2d");
    new Chart(ctx, {
      type: chartData.type,
      data: chartData.data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: chartData.title,
          },
          tooltip: {
            enabled: true,
          },
        },
        scales:
          chartData.type !== "pie" && chartData.type !== "radar"
            ? {
                y: {
                  beginAtZero: true,
                },
              }
            : {},
      },
    });

    // Add description
    const descriptionEl = document.createElement("p");
    descriptionEl.className = "chart-description";
    descriptionEl.textContent = chartData.description;
    container.appendChild(descriptionEl);
  } catch (error) {
    console.error(`Error loading chart from ${jsonFile}:`, error);
  }
}

// Function to fetch and load all JSON files from the data directory
async function loadAllCharts() {
  try {
    // Fetch the list of chart files from chart_files.json
    const response = await fetch("data/chart_files.json");
    const { charts } = await response.json();

    // Create charts for each JSON file in the list
    for (const file of charts) {
      await createChart(file);
    }
  } catch (error) {
    console.error("Error loading charts:", error);
  }
}

// Load all charts when the document is ready
document.addEventListener("DOMContentLoaded", loadAllCharts);
