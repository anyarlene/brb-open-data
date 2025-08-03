export const getChartConfig = (type, data, options, title, year) => {
  // Professional color palette for charts
  const chartColors = [
    "#2a6f86", // Primary blue
    "#f0b429", // Gold
    "#e85d04", // Orange
    "#2b9348", // Green
    "#6930c3", // Purple
  ];

  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: `${title} - ${year}`,
        font: {
          size: 16,
          weight: "bold",
          family: "'Inter', sans-serif",
        },
        padding: {
          top: 10,
          bottom: 20,
        },
        color: "#1e4d5c", // primary-color
      },
      legend: {
        position: "top",
        align: "center",
        labels: {
          boxWidth: 12,
          padding: 15,
          font: {
            size: 11,
            family: "'Inter', sans-serif",
          },
          color: "#1a2b32", // text-color
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const value = context.raw.toLocaleString("en-US", {
              maximumFractionDigits: 0,
            });
            return `${context.dataset.label}: ${value} M BIF`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: "#e1e8ed", // gray-200
          drawBorder: false,
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45,
          font: {
            size: 10,
            family: "'Inter', sans-serif",
          },
          color: "#4a6271", // text-light
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: "#e1e8ed", // gray-200
          drawBorder: false,
        },
        ticks: {
          font: {
            size: 10,
            family: "'Inter', sans-serif",
          },
          color: "#4a6271", // text-light
          callback: function (value) {
            return (
              value.toLocaleString("en-US", {
                maximumFractionDigits: 0,
              }) + " M"
            );
          },
        },
        title: {
          display: true,
          text: "Million BIF",
          color: "#1a2b32",
          font: {
            size: 12,
            family: "'Inter', sans-serif",
            weight: "500",
          },
        },
      },
    },
    layout: {
      padding: {
        left: 15,
        right: 15,
        top: 5,
        bottom: 5,
      },
    },
    elements: {
      line: {
        tension: 0.3, // Smooth lines
      },
      point: {
        radius: 4,
        hitRadius: 8,
        hoverRadius: 6,
      },
    },
  };

  // Override the dataset colors with our professional palette
  if (data.datasets) {
    data.datasets = data.datasets.map((dataset, index) => ({
      ...dataset,
      backgroundColor: chartColors[index % chartColors.length],
      borderColor: chartColors[index % chartColors.length],
      borderWidth: 2,
      fill: false,
    }));
  }

  return {
    type,
    data,
    options: {
      ...defaultOptions,
      ...options,
      plugins: {
        ...defaultOptions.plugins,
        ...(options?.plugins || {}),
      },
    },
  };
};
