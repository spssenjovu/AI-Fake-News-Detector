document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("news-form");
  const input = document.getElementById("news");
  const resultsContainer = document.getElementById("results");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const rawInput = input.value.trim();
    if (!rawInput) {
      resultsContainer.innerHTML = "<p>Please enter at least one news URL.</p>";
      return;
    }

    const urls = rawInput.split(/\s+/);
    const query = urls.map(u => `urls=${encodeURIComponent(u)}`).join("&");

    resultsContainer.innerHTML = `<p>🔍 Analyzing ${urls.length} article${urls.length > 1 ? "s" : ""}...</p>`;

    try {
      const response = await fetch(`/predict-news?${query}`);
      if (!response.ok) throw new Error(`Server responded with ${response.status}`);

      const data = await response.json();
      resultsContainer.innerHTML = "";

      if (!data.results || data.results.length === 0) {
        resultsContainer.innerHTML = "<p>No prediction results found.</p>";
        return;
      }

      data.results.forEach(article => {
        const card = document.createElement("div");
        card.className = "result-card";

        const color = article.classification === "Fake" ? "red" :
                      article.classification === "Real" ? "green" : "gray";

        card.innerHTML = `
          <h3><a href="${article.url}" target="_blank">${article.url}</a></h3>
          <p><strong>Prediction:</strong> <span style="color:${color}">${article.classification}</span>
             (Confidence: ${article.confidence})</p>
          ${article.credibility_score !== undefined
            ? `<p><strong>Credibility Score:</strong> ${article.credibility_score}</p>` : ""}
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