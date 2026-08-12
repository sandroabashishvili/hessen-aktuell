const analyticsConsentScript = document.createElement("script");
analyticsConsentScript.src = new URL("analytics-consent.js", document.currentScript.src).href;
analyticsConsentScript.defer = true;
document.head.appendChild(analyticsConsentScript);

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
const jobList = document.getElementById("jobs-list");
const jobCards = Array.from(document.querySelectorAll("[data-job-search]"));
const jobResultCount = document.getElementById("job-result-count");
const jobResultLabel = document.getElementById("job-result-label");
const jobEmpty = document.getElementById("jobs-empty");
const jobPagination = document.getElementById("job-pagination");
const jobPagePrev = document.getElementById("job-page-prev");
const jobPageNext = document.getElementById("job-page-next");
const jobPageStatus = document.getElementById("job-page-status");
const jobPageSize = Number(jobList?.dataset.pageSize || 8);
let jobCurrentPage = 1;

const normalizeFilterText = (value) =>
  value
    .toLocaleLowerCase("de")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .trim();

const applyJobFilters = ({ resetPage = false, scrollToResults = false } = {}) => {
  if (!jobList) {
    return;
  }
  if (resetPage) {
    jobCurrentPage = 1;
  }

  const query = normalizeFilterText(jobSearch?.value || "");
  const city = jobCity?.value || "";
  const category = jobCategory?.value || "";
  const matchingCards = jobCards.filter((card) => {
    const matchesQuery = !query || card.dataset.jobSearch.includes(query);
    const matchesCity = !city || card.dataset.jobCity === city;
    const matchesCategory = !category || card.dataset.jobCategory === category;
    return matchesQuery && matchesCity && matchesCategory;
  });
  const totalMatches = matchingCards.length;
  const totalPages = Math.max(1, Math.ceil(totalMatches / jobPageSize));
  jobCurrentPage = Math.min(jobCurrentPage, totalPages);
  const pageStart = (jobCurrentPage - 1) * jobPageSize;
  const pageCards = new Set(
    matchingCards.slice(pageStart, pageStart + jobPageSize)
  );
  jobCards.forEach((card) => {
    card.hidden = !pageCards.has(card);
  });

  if (jobResultCount) {
    jobResultCount.textContent = String(totalMatches);
  }
  if (jobResultLabel) {
    jobResultLabel.textContent =
      totalMatches === 1 ? "Stelle gefunden" : "Stellen gefunden";
  }
  if (jobEmpty) {
    jobEmpty.hidden = totalMatches !== 0;
  }
  if (jobPagination) {
    jobPagination.hidden = totalMatches <= jobPageSize;
  }
  if (jobPageStatus) {
    jobPageStatus.textContent = `Seite ${jobCurrentPage} von ${totalPages}`;
  }
  if (jobPagePrev) {
    jobPagePrev.disabled = jobCurrentPage <= 1;
  }
  if (jobPageNext) {
    jobPageNext.disabled = jobCurrentPage >= totalPages;
  }
  if (scrollToResults) {
    document.querySelector(".jobs-result-line")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }
};

if (jobList) {
  jobSearch?.addEventListener("input", () => applyJobFilters({ resetPage: true }));
  jobCity?.addEventListener("change", () => applyJobFilters({ resetPage: true }));
  jobCategory?.addEventListener("change", () => applyJobFilters({ resetPage: true }));

  jobReset?.addEventListener("click", () => {
    if (jobSearch) jobSearch.value = "";
    if (jobCity) jobCity.value = "";
    if (jobCategory) jobCategory.value = "";
    applyJobFilters({ resetPage: true });
    jobSearch?.focus();
  });

  jobPagePrev?.addEventListener("click", () => {
    jobCurrentPage -= 1;
    applyJobFilters({ scrollToResults: true });
  });
  jobPageNext?.addEventListener("click", () => {
    jobCurrentPage += 1;
    applyJobFilters({ scrollToResults: true });
  });

  applyJobFilters();
}
