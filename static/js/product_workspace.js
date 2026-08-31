(() => {
  "use strict";

  let pendingControlId = null;

  const workspaceControl = (event) => {
    const element = event.detail?.elt;
    return element?.matches?.("[data-workspace-stock-button]")
      ? element
      : null;
  };

  const currentResults = () =>
    document.getElementById("product-workspace-results");

  const hideTransportRecovery = () => {
    const recovery = document.getElementById(
      "product-workspace-transport-error",
    );
    if (recovery) {
      recovery.hidden = true;
    }
  };

  const showTransportRecovery = () => {
    const results = currentResults();
    if (results) {
      results.setAttribute("aria-busy", "false");
    }
    const recovery = document.getElementById(
      "product-workspace-transport-error",
    );
    if (recovery) {
      recovery.hidden = false;
      recovery.focus();
    }
    pendingControlId = null;
  };

  document.body.addEventListener("htmx:beforeRequest", (event) => {
    const control = workspaceControl(event);
    if (!control) {
      return;
    }
    pendingControlId = control.id;
    hideTransportRecovery();
    currentResults()?.setAttribute("aria-busy", "true");
  });

  document.body.addEventListener("htmx:afterSwap", (event) => {
    if (event.detail?.target?.id !== "product-workspace-results") {
      return;
    }

    const results = currentResults();
    results?.setAttribute("aria-busy", "false");
    const restoredControl = pendingControlId
      ? document.getElementById(pendingControlId)
      : null;
    if (restoredControl) {
      restoredControl.focus();
    } else {
      document.getElementById("product-workspace-stock-status")?.focus();
    }
    pendingControlId = null;
  });

  document.body.addEventListener("htmx:afterRequest", (event) => {
    if (workspaceControl(event) && event.detail?.successful === false) {
      showTransportRecovery();
    }
  });

  for (const eventName of ["htmx:sendError", "htmx:timeout", "htmx:swapError"]) {
    document.body.addEventListener(eventName, (event) => {
      if (workspaceControl(event)) {
        showTransportRecovery();
      }
    });
  }
})();
