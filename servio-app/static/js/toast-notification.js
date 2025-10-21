function showToast(message, type = "success", title) {
  const container = document.getElementById("toast-container");

  const types = {
    success: {
      title: title || "Success",
      border: "border-green-500",
      bg: "bg-green-50",
      text: "text-green-500",
      titleColor: "text-green-800",
      icon: `<svg class="fill-current" width="24" height="24" viewBox="0 0 24 24">
                 <path d="M12 0a12 12 0 1 0 12 12A12.013 12.013 0 0 0 12 0Zm-1 17.414-4.707-4.707L7.707 11l3.293 3.293L16.293 9l1.414 1.414Z"/>
               </svg>`,
    },
    error: {
      title: title || "Error",
      border: "border-red-500",
      bg: "bg-red-50",
      text: "text-red-500",
      titleColor: "text-red-800",
      icon: `<svg class="fill-current" width="24" height="24" viewBox="0 0 24 24">
                 <path d="M12 0a12 12 0 1 0 12 12A12.013 12.013 0 0 0 12 0Zm5 15.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12Z"/>
               </svg>`,
    },
    warning: {
      title: title || "Warning",
      border: "border-yellow-500",
      bg: "bg-yellow-50",
      text: "text-yellow-500",
      titleColor: "text-yellow-800",
      icon: `<svg class="fill-current" width="24" height="24" viewBox="0 0 24 24">
                 <path d="M1 21h22L12 2 1 21Zm12-3h-2v-2h2v2Zm0-4h-2v-4h2v4Z"/>
               </svg>`,
    },
    info: {
      title: title || "Info",
      border: "border-blue-500",
      bg: "bg-blue-50",
      text: "text-blue-500",
      titleColor: "text-blue-800",
      icon: `<svg class="fill-current" width="24" height="24" viewBox="0 0 24 24">
                 <path d="M12 2a10 10 0 1 0 10 10A10.011 10.011 0 0 0 12 2Zm.25 15h-1.5v-6h1.5v6Zm0-8h-1.5V7h1.5v2Z"/>
               </svg>`,
    },
  };

  const t = types[type] || types.success;

  const toast = document.createElement("div");
  toast.className = `
      rounded-xl border ${t.border} ${t.bg} p-4 shadow-lg w-auto max-w-sm
      opacity-0 transform -translate-y-4 transition-all duration-500 ease-in-out
    `;

  toast.innerHTML = `
      <div class="flex items-start gap-3 mx-3">
        <div class="${t.text}">${t.icon}</div>
        <div>
          <h4 class="mb-1 text-sm font-semibold ${t.titleColor}">${t.title}</h4>
          <p class="text-xs md:text-sm ${t.titleColor}">${message}</p>
        </div>
      </div>
    `;

  container.appendChild(toast);

  // Fade in animation
  setTimeout(() => {
    toast.classList.remove("opacity-0", "-translate-y-4");
    toast.classList.add("opacity-100", "translate-y-0");
  }, 50);

  // Auto-remove after 6s
  setTimeout(() => {
    toast.classList.remove("opacity-100", "translate-y-0");
    toast.classList.add("opacity-0", "-translate-y-4");
    setTimeout(() => toast.remove(), 500);
  }, 6000);
}

// Example usage
// document.addEventListener("DOMContentLoaded", () => {
//   showToast("Operation completed successfully.", "success");
//   setTimeout(() => showToast("Be careful with this action.", "warning"), 1000);
//   setTimeout(() => showToast("Here’s some information.", "info"), 2000);
//   setTimeout(() => showToast("Something went wrong!", "error"), 3000);
// });
