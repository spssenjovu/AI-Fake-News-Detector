document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("news-form");
  const input = document.getElementById("news");
  const resultsContainer = document.getElementById("results");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const rawInput = input.value.trim();
    if (!rawInput) return;

    const urls = rawInput.split(/\s+/);
    const query = urls.map(u => `urls=${encodeURIComponent(u)}`).join("&");

    // Show loading state
    resultsContainer.innerHTML = `<p>🔍 Analysing ${urls.length} article${urls.length > 1 ? "s" : ""}...</p>`;

    try {
      const response = await fetch(`/predict-news?${query}`);
      const data = await response.json();

      // Clear previous results
      resultsContainer.innerHTML = "";

      if (!data.results || data.results.length === 0) {
        resultsContainer.innerHTML = "<p>No prediction results found.</p>";
        return;
      }

      data.results.forEach(article => {
        const card = document.createElement("div");
        card.className = "result-card";

        card.innerHTML = `
          <h3><a href="${article.url}" target="_blank">${article.url}</a></h3>
          <p><strong>Prediction:</strong> ${article.classification} (Confidence: ${article.confidence})</p>
          ${article.credibility_score !== undefined ? `<p><strong>Credibility Score:</strong> ${article.credibility_score}</p>` : ""}
          <p><strong>Source Trust:</strong> ${article.trust_level} — ${article.source}</p>
          <p><strong>Explanation:</strong> ${article.explanation}</p>
          <p class="version">Model Version: ${article.model_version}</p>
        `;

        resultsContainer.appendChild(card);
      });
    } catch (error) {
      console.error("Error fetching prediction:", error);
      resultsContainer.innerHTML = "<p> Failed to fetch prediction. Please try again later.</p>";
    }
  });
});