function getTabFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get("tab") || "register";
  }

const switchTab = (tab) => {
	window.location.href = `?tab=${tab}`;
}

// Automatically activate the right tab on load
window.onload = () => {
    const tab = getTabFromURL();

    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll("form").forEach(f => f.classList.remove("active"));

    if (tab === "login") {
      document.getElementById("loginForm").classList.add("active");
      document.querySelector(".tab[data-tab='login']").classList.add("active");
    } else {
      document.getElementById("registerForm").classList.add("active");
      document.querySelector(".tab[data-tab='register']").classList.add("active");
    }
  };