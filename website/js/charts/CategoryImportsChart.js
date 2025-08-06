class CategoryImportsChart extends BaseChart {
  constructor(containerId) {
    super(containerId);
    this.data = null;
    this.yearSlider = null;
    this.yearDisplay = null;
  }

  async initialize() {
    try {
      console.log("Initializing CategoryImportsChart...");
      // Fetch the chart data
      const response = await fetch("data/monthly_imports_by_category.json");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      this.data = await response.json();
      console.log("Category data loaded:", this.data);

      // Set up year slider and get initial year
      const initialYear = this.setupYearSlider();

      // Initialize chart with the initial year
      this.updateChart(initialYear);

      // Add window resize handler
      this.handleResize();
    } catch (error) {
      console.error("Error initializing category visualization:", error);
    }
  }

  handleResize() {
    let resizeTimer;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        this.updateChart(this.data.years[this.yearSlider.value]);
      }, 250);
    });
  }

  setupYearSlider() {
    this.yearSlider = document.getElementById("categoryYearSlider");
    this.yearDisplay = document.getElementById("categorySelectedYear");

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

    // Get responsive configuration
    const config = getChartConfig(
      this.data.type,
      yearData,
      this.data.options,
      this.data.title,
      year
    );

    // Create new chart instance
    this.chart = new Chart(ctx, config);
  }
}