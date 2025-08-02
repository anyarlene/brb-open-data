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

// List of JSON files to load
const chartFiles = [
  "monthly_imports.json",
  "sector_distribution.json",
  "country_comparison.json",
  "quarterly_growth.json",
  "yearly_comparison.json",
];

// Load all charts when the document is ready
document.addEventListener("DOMContentLoaded", () => {
  chartFiles.forEach((file) => createChart(file));
});
