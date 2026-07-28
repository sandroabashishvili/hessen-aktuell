document.documentElement.classList.add("js-ready");

const siteHeader = document.querySelector(".site-header");
const navToggle = document.querySelector(".nav-toggle");
const siteNav = document.getElementById("site-nav");

if (siteHeader && navToggle && siteNav) {
  navToggle.addEventListener("click", () => {
    const isOpen = siteHeader.classList.toggle("nav-open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });

  siteNav.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      siteHeader.classList.remove("nav-open");
      navToggle.setAttribute("aria-expanded", "false");
    }
  });
}

const jobSearch = document.getElementById("job-search");
const jobCity = document.getElementById("job-city");
const jobCategory = document.getElementById("job-category");
const jobReset = document.getElementById("job-filter-reset");
const jobCards = Array.from(document.querySelectorAll("[data-job-search]"));
const jobResultCount = document.getElementById("job-result-count");
const jobResultLabel = document.getElementById("job-result-label");
const jobEmpty = document.getElementById("jobs-empty");

const normalizeFilterText = (value) =>
  value
    .toLocaleLowerCase("de")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .trim();

const applyJobFilters = () => {
  if (!jobSearch || !jobCity || !jobCategory) {
    return;
  }

  const query = normalizeFilterText(jobSearch.value);
  const city = jobCity.value;
  const category = jobCategory.value;
  let visible = 0;

  jobCards.forEach((card) => {
    const matchesQuery = !query || card.dataset.jobSearch.includes(query);
    const matchesCity = !city || card.dataset.jobCity === city;
    const matchesCategory = !category || card.dataset.jobCategory === category;
    const matches = matchesQuery && matchesCity && matchesCategory;
    card.hidden = !matches;
    if (matches) {
      visible += 1;
    }
  });

  if (jobResultCount) {
    jobResultCount.textContent = String(visible);
  }
  if (jobResultLabel) {
    jobResultLabel.textContent = visible === 1 ? "Stelle gefunden" : "Stellen gefunden";
  }
  if (jobEmpty) {
    jobEmpty.hidden = visible !== 0;
  }
};

if (jobSearch && jobCity && jobCategory) {
  jobSearch.addEventListener("input", applyJobFilters);
  jobCity.addEventListener("change", applyJobFilters);
  jobCategory.addEventListener("change", applyJobFilters);

  jobReset?.addEventListener("click", () => {
    jobSearch.value = "";
    jobCity.value = "";
    jobCategory.value = "";
    applyJobFilters();
    jobSearch.focus();
  });
}
