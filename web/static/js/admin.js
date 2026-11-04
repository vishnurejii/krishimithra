/**
 * KrishiMitra AI - Admin Dashboard JavaScript
 * Displays KPIs, live Coverage Matrix across 62 departments,
 * Document Explorer, Scheme Verification Studio, and Manual Crawl Trigger.
 */

document.addEventListener("DOMContentLoaded", () => {
  loadAdminMetrics();
  loadCoverageMatrix();
  setupCrawlTriggerForm();
});

// Load Metrics
async function loadAdminMetrics() {
  try {
    const resp = await fetch("/api/admin/metrics/");
    const data = await resp.json();
    if (data.status === "success") {
      const m = data.metrics;
      document.getElementById("metricTotalDocs").textContent = m.total_documents;
      document.getElementById("metricProcessedDocs").textContent = m.processed_documents;
      document.getElementById("metricTotalSchemes").textContent = m.total_schemes;
      document.getElementById("metricActiveSchemes").textContent = m.active_schemes;
      document.getElementById("metricPendingVerification").textContent = m.pending_verification;
      document.getElementById("metricExpiredSchemes").textContent = m.expired_schemes;

      // Render recent documents
      const recContainer = document.getElementById("recentDocsContainer");
      if (recContainer && data.recent_documents) {
        recContainer.innerHTML = data.recent_documents.map(d => `
          <tr>
            <td><strong>${d.title}</strong></td>
            <td><a href="${d.original_url}" target="_blank" style="color: #059669; text-decoration: none;">View Original</a></td>
            <td><span class="badge ${d.processing_status === 'PROCESSED' ? 'badge-active' : 'badge-pending'}">${d.processing_status}</span></td>
            <td>${d.doc_type}</td>
            <td>${d.created_at ? d.created_at.split('T')[0] : ''}</td>
          </tr>
        `).join("");
      }
    }
  } catch (err) {
    console.error("Error loading metrics:", err);
  }
}

// Load Coverage Matrix
async function loadCoverageMatrix(statusFilter = '') {
  const container = document.getElementById("coverageTableBody");
  container.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 2rem;">Loading Scheme Coverage Matrix across agriculture portals...</td></tr>`;

  // Update active pill styling
  document.querySelectorAll(".card .pill").forEach(p => p.classList.remove("active"));
  const clicked = window.event && window.event.target ? window.event.target : null;
  if (clicked && clicked.classList.contains("pill")) clicked.classList.add("active");

  try {
    const resp = await fetch("/api/coverage/matrix/");
    const data = await resp.json();
    let matrix = data.matrix || [];

    if (statusFilter) {
      matrix = matrix.filter(m => m.investigation_status === statusFilter);
    }

    container.innerHTML = matrix.map(m => {
      let badgeClass = "badge-pending";
      if (m.investigation_status === "Verified") badgeClass = "badge-active";
      else if (m.investigation_status === "Documents collected") badgeClass = "badge-subsidy";
      else if (m.investigation_status === "No relevant schemes found") badgeClass = "badge-expired";

      return `
        <tr>
          <td>
            <strong>${m.department_name}</strong>
            <div style="font-size: 0.75rem; color: #64748b;">${m.level} &bull; ${m.category}</div>
          </td>
          <td><span class="badge ${badgeClass}">${m.investigation_status}</span></td>
          <td style="text-align: center; font-weight: 700;">${m.documents_discovered}</td>
          <td style="text-align: center; font-weight: 700;">${m.schemes_identified}</td>
          <td style="text-align: center; font-weight: 700; color: #059669;">${m.active_schemes_verified}</td>
          <td><a href="${m.official_website}" target="_blank" style="color:#059669; font-weight:600;">Visit Portal</a></td>
          <td style="font-size: 0.8rem; color: #64748b;">${m.missing_information || 'Complete'}</td>
          <td>
            <button onclick="triggerCrawlFor('${m.department_id}')" style="background: #f1f5f9; border: 1px solid #cbd5e1; padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.8rem; cursor: pointer;">
              Crawl
            </button>
          </td>
        </tr>
      `;
    }).join("");

  } catch (err) {
    container.innerHTML = `<tr><td colspan="8" style="color: red;">Error: ${err}</td></tr>`;
  }
}

// Manual Crawl Trigger
function setupCrawlTriggerForm() {
  const btn = document.getElementById("manualCrawlBtn");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const deptId = document.getElementById("crawlDeptSelect").value;
    triggerCrawlFor(deptId);
  });
}

async function triggerCrawlFor(deptId) {
  const statusElem = document.getElementById("crawlStatusMsg");
  if (statusElem) {
    statusElem.style.display = "block";
    statusElem.textContent = `Running live crawler adapter for ${deptId}... Please wait...`;
  }

  try {
    const resp = await fetch("/api/admin/crawl/trigger/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ department_id: deptId })
    });
    const data = await resp.json();
    if (data.status === "success") {
      if (statusElem) statusElem.textContent = `Crawl successful! Discovered ${data.discovered_count} documents for ${deptId}.`;
      loadAdminMetrics();
      loadCoverageMatrix();
    } else {
      if (statusElem) statusElem.textContent = `Crawl failed: ${data.message}`;
    }
  } catch (err) {
    if (statusElem) statusElem.textContent = `Error: ${err}`;
  }
}

// Scheme Approval / Rejection
async function verifyScheme(schemeId, action) {
  if (!confirm(`Are you sure you want to ${action} this scheme?`)) return;

  try {
    const resp = await fetch(`/api/admin/schemes/${schemeId}/verify/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: action, reason: "Manual Admin Studio Review" })
    });
    const data = await resp.json();
    alert(data.message || "Updated successfully");
    loadAdminMetrics();
  } catch (err) {
    alert(`Error: ${err}`);
  }
}
