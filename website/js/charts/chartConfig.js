export const getChartConfig = (type, data, options, title, year) => {
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
        },
        padding: {
          top: 10,
          bottom: 20,
        },
      },
      legend: {
        position: "top",
        align: "center",
        labels: {
          boxWidth: 12,
          padding: 15,
          font: {
            size: 11,
          },
        },
      },
    },
    scales: {
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45,
          font: {
            size: 10,
          },
        },
      },
      y: {
        beginAtZero: true,
        ticks: {
          font: {
            size: 10,
          },
        },
      },
    },
    layout: {
      padding: {
        left: 10,
        right: 10,
      },
    },
  };

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
