(() => {
  "use strict";

  let pendingControlId = null;

  const workspaceFormFields = [
    {
      fieldId: "id_q",
      helpTextId: "id_q_helptext",
      errorId: "id_q_errors",
    },
    {
      fieldId: "id_lifecycle",
      errorId: "id_lifecycle_errors",
    },
    {
      fieldId: "id_availability",
      errorId: "id_availability_errors",
    },
  ];

  const workspaceControl = (event) => {
    const element = event.detail?.elt;
    return element?.matches?.("[data-workspace-stock-button]")
      ? element
      : null;
  };

  const currentResults = () =>
    document.getElementById("product-workspace-results");

  const syncWorkspaceFormAccessibility = () => {
    for (const { fieldId, helpTextId, errorId } of workspaceFormFields) {
      const field = document.getElementById(fieldId);
      if (!field) {
        continue;
      }

      const describedBy = [helpTextId, errorId]
        .filter((id) => id && document.getElementById(id))
        .join(" ");
      if (describedBy) {
        field.setAttribute("aria-describedby", describedBy);
      } else {
        field.removeAttribute("aria-describedby");
      }

      const error = errorId && document.getElementById(errorId);
      if (error) {
        field.setAttribute("aria-invalid", "true");
        field.setAttribute("aria-errormessage", errorId);
      } else {
        field.removeAttribute("aria-invalid");
        field.removeAttribute("aria-errormessage");
      }
    }
  };

  const setWorkspaceActionBusy = (control, isBusy) => {
    const form = control?.closest("form");
    if (!form) {
      return;
    }

    form.setAttribute("aria-busy", String(isBusy));
    for (const button of form.querySelectorAll(
      "[data-workspace-stock-button]",
    )) {
      if (isBusy) {
        button.setAttribute("aria-disabled", "true");
      } else {
        button.removeAttribute("aria-disabled");
      }
    }
  };

  const pendingControl = () =>
    pendingControlId ? document.getElementById(pendingControlId) : null;

  const hideTransportRecovery = () => {
    const recovery = document.getElementById(
      "product-workspace-transport-error",
    );
    if (recovery) {
      recovery.hidden = true;
    }
  };

  const showTransportRecovery = () => {
    setWorkspaceActionBusy(pendingControl(), false);
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
    setWorkspaceActionBusy(control, true);
    currentResults()?.setAttribute("aria-busy", "true");
  });

  document.body.addEventListener("htmx:afterSwap", (event) => {
    if (event.detail?.target?.id !== "product-workspace-results") {
      return;
    }

    const results = currentResults();
    results?.setAttribute("aria-busy", "false");
    const restoredControl = pendingControl();
    setWorkspaceActionBusy(restoredControl, false);
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

  syncWorkspaceFormAccessibility();
})();
