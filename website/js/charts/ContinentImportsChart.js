import { BaseChart } from "./BaseChart.js";

export class ContinentImportsChart extends BaseChart {
  constructor(containerId) {
    super(containerId);
    this.data = null;
    this.yearSlider = null;
    this.yearDisplay = null;
  }

  async initialize() {
    try {
      // Fetch the chart data
      const response = await fetch("data/monthly_imports_by_continent.json");
      this.data = await response.json();

      // Set up year slider and get initial year
      const initialYear = this.setupYearSlider();

      // Initialize chart with the initial year
      this.updateChart(initialYear);
    } catch (error) {
      console.error("Error initializing visualization:", error);
    }
  }

  setupYearSlider() {
    this.yearSlider = document.getElementById("yearSlider");
    this.yearDisplay = document.getElementById("selectedYear");

    // Configure slider
    this.yearSlider.min = 0;
    this.yearSlider.max = this.data.years.length - 1;
    this.yearSlider.value = this.data.years.length - 1; // Start with most recent year
    this.yearSlider.step = 1;

    // Update selected year display
    this.yearDisplay.textContent = this.data.years[this.yearSlider.value];

    // Add event listeners
    this.yearSlider.addEventListener("input", (e) => {
      const selectedYear = this.data.years[e.target.value];
      this.yearDisplay.textContent = selectedYear;
      this.updateChart(selectedYear);
    });

    return this.data.years[this.yearSlider.value];
  }

  updateChart(year) {
    this.destroy();

    const ctx = document.getElementById(this.containerId).getContext("2d");
    const yearData = this.data.data[year];

    const config = {
      type: this.data.type,
      data: yearData,
      options: this.data.options,
    };

    // Parse tooltip callback if exists
    config.options = this.parseTooltipCallback(config.options);

    // Update the chart title with the selected year
    config.options.plugins.title.text = `${this.data.title} - ${year}`;

    this.chart = new Chart(ctx, config);
  }
}
