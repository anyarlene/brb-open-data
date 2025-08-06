class BaseChart {
  constructor(containerId) {
    this.containerId = containerId;
    this.chart = null;
  }

  destroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }

  parseTooltipCallback(options) {
    if (options?.plugins?.tooltip?.callbacks?.label) {
      const labelFnStr = options.plugins.tooltip.callbacks.label;
      options.plugins.tooltip.callbacks.label = new Function(
        "return " + labelFnStr
      )();
    }
    return options;
  }
}