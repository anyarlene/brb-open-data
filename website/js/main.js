// Initialize all charts when the document is ready
document.addEventListener("DOMContentLoaded", async () => {
  // Initialize the continent imports chart
  const continentChart = new ContinentImportsChart("importChart");
  await continentChart.initialize();
});