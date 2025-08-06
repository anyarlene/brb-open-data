document.addEventListener("DOMContentLoaded", async () => {
  // Initialize both charts
  const continentChart = new ContinentImportsChart("importChart");
  const categoryChart = new CategoryImportsChart("categoryChart");
  
  await continentChart.initialize();
  await categoryChart.initialize();

  // Handle visualization toggle
  const vizBtns = document.querySelectorAll('.viz-btn');
  const vizContainers = document.querySelectorAll('.visualization-container');
  const dropdownBtn = document.querySelector('.dropdown-btn');
  const dropdownContent = document.querySelector('.dropdown-content');

  // Function to update visualization
  const updateVisualization = (btn) => {
    // Update buttons
    vizBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Update containers
    const targetViz = btn.dataset.viz;
    vizContainers.forEach(container => {
      container.classList.remove('active');
      if (container.id === `${targetViz}Viz`) {
        container.classList.add('active');
      }
    });

    // Update dropdown button text to "Statistics ▾"
    dropdownBtn.textContent = 'Statistics ▾';
  };

  // Handle button clicks
  vizBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      updateVisualization(btn);
    });
  });

  // Set initial state
  const activeBtn = document.querySelector('.viz-btn.active');
  if (activeBtn) {
    dropdownBtn.textContent = 'Statistics ▾';
  }

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!dropdownBtn.contains(e.target) && !dropdownContent.contains(e.target)) {
      dropdownContent.style.display = 'none';
    }
  });

  // Toggle dropdown on button click
  dropdownBtn.addEventListener('click', (e) => {
    e.preventDefault();
    const isVisible = dropdownContent.style.display === 'block';
    dropdownContent.style.display = isVisible ? 'none' : 'block';
  });
});