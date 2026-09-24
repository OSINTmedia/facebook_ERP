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

  const readyReplyControl = (event) => {
    const element = event.detail?.elt;
    return element?.matches?.("[data-ready-reply-trigger]")
      ? element
      : null;
  };

  const currentResults = () =>
    document.getElementById("product-workspace-results");

  const syncFieldErrors = (root = document) => {
    let generatedErrorId = 0;
    for (const container of root.querySelectorAll(".form-field")) {
      const field = container.querySelector("input, select, textarea");
      const error = container.querySelector(".field-error, .form-errors");
      if (!field || !error) {
        continue;
      }
      if (!error.id) {
        generatedErrorId += 1;
        error.id = `${field.id || "field"}-error-${generatedErrorId}`;
      }
      error.setAttribute("role", "alert");
      field.setAttribute("aria-invalid", "true");
      field.setAttribute("aria-errormessage", error.id);
      const describedBy = new Set(
        (field.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean),
      );
      describedBy.add(error.id);
      field.setAttribute("aria-describedby", [...describedBy].join(" "));
    }
  };

  const productFormControl = (event) => {
    const element = event.detail?.elt;
    return element?.closest?.(".product-form") ? element : null;
  };

  const setProductFormBusy = (control, isBusy) => {
    control?.closest?.(".product-form")?.setAttribute("aria-busy", String(isBusy));
  };

  const hideProductFormTransportRecovery = () => {
    const recovery = document.getElementById("product-form-transport-error");
    if (recovery) {
      recovery.hidden = true;
    }
  };

  const showProductFormTransportRecovery = (control) => {
    setProductFormBusy(control, false);
    const recovery = document.getElementById("product-form-transport-error");
    if (recovery) {
      recovery.hidden = false;
      recovery.focus();
    }
  };

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
        button.disabled = true;
        button.setAttribute("aria-disabled", "true");
      } else {
        button.disabled = false;
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

  const readyReplyError = (control) => {
    const productId = control?.id?.replace("product-ready-reply-trigger-", "");
    return productId
      ? document.getElementById(`product-ready-reply-error-${productId}`)
      : null;
  };

  const readyReplySlot = (control) => {
    const targetSelector = control?.getAttribute("hx-target");
    return targetSelector ? document.querySelector(targetSelector) : null;
  };

  const hideReadyReplyTransportRecovery = (control) => {
    control.setAttribute("aria-expanded", "false");
    readyReplySlot(control)?.replaceChildren();
    const error = readyReplyError(control);
    if (error) {
      error.hidden = true;
    }
  };

  const showReadyReplyTransportRecovery = (control) => {
    if (!control) {
      return;
    }
    control.setAttribute("aria-expanded", "false");
    readyReplySlot(control)?.replaceChildren();
    const error = readyReplyError(control);
    if (error) {
      error.hidden = false;
      error.focus();
    }
  };

  const openDecks = new Set();

  const toggleDeck = (toggleBtn) => {
    const deckId = toggleBtn.getAttribute("aria-controls");
    const deck = document.getElementById(deckId);
    if (!deck) {
      return;
    }
    const isExpanded = toggleBtn.getAttribute("aria-expanded") === "true";
    const nextState = !isExpanded;
    toggleBtn.setAttribute("aria-expanded", String(nextState));
    deck.hidden = !nextState;
    if (nextState) {
      openDecks.add(deckId);
    } else {
      openDecks.delete(deckId);
    }
    const icon = toggleBtn.querySelector(".product-card__deck-toggle-icon");
    if (icon) {
      icon.textContent = nextState ? "▲" : "▼";
    }
  };

  const syncDeckState = (root = document) => {
    const results = currentResults();
    const focusChoiceId = results?.dataset.workspaceFocusChoiceId;

    for (const toggleBtn of root.querySelectorAll("[data-deck-toggle]")) {
      const deckId = toggleBtn.getAttribute("aria-controls");
      const deck = document.getElementById(deckId);
      if (!deck) {
        continue;
      }

      let shouldBeOpen = openDecks.has(deckId);
      if (
        focusChoiceId &&
        deck.querySelector(`#workspace-stock-decrease-${focusChoiceId}`)
      ) {
        shouldBeOpen = true;
        openDecks.add(deckId);
      }

      toggleBtn.setAttribute("aria-expanded", String(shouldBeOpen));
      deck.hidden = !shouldBeOpen;
      const icon = toggleBtn.querySelector(".product-card__deck-toggle-icon");
      if (icon) {
        icon.textContent = shouldBeOpen ? "▲" : "▼";
      }
    }
  };

  const closeReadyReply = (element) => {
    const root = element?.closest("[data-ready-reply-root]") || document.getElementById("product-ready-reply-root");
    const triggerId = root?.dataset.readyReplyTriggerId;
    const trigger = triggerId ? document.getElementById(triggerId) : null;
    if (root) {
      const mount = root.closest("[data-ready-reply-mount]") || root.parentElement;
      if (mount && mount.id === "ready-reply-root") {
        mount.replaceChildren();
      } else {
        root.remove();
      }
    }
    if (trigger) {
      trigger.setAttribute("aria-expanded", "false");
      trigger.focus();
    }
  };

  const setupInstantMediaPreview = (root = document) => {
    const fileInput = root.querySelector?.('input[type="file"][name="image"]');
    if (!fileInput || fileInput.dataset.previewAttached) {
      return;
    }
    fileInput.dataset.previewAttached = "true";

    fileInput.addEventListener("change", () => {
      const file = fileInput.files?.[0];
      const previewImg = document.getElementById("product-media-preview-img");
      const placeholder = document.getElementById("product-media-preview-placeholder");

      if (file && file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = (e) => {
          if (previewImg) {
            previewImg.src = e.target?.result;
            previewImg.hidden = false;
          }
          if (placeholder) {
            placeholder.hidden = true;
          }
        };
        reader.readAsDataURL(file);
      } else if (!file) {
        if (previewImg?.dataset.defaultSrc) {
          previewImg.src = previewImg.dataset.defaultSrc;
          previewImg.hidden = false;
          if (placeholder) placeholder.hidden = true;
        } else {
          if (previewImg) previewImg.hidden = true;
          if (placeholder) placeholder.hidden = false;
        }
      }
    });
  };

  const syncVocabularyCardAccessibility = (root = document) => {
    const card = root.querySelector?.("#choice-vocabulary-card");
    if (!card) return;
    const summary = card.querySelector("#vocabulary-card-summary");
    if (!summary) return;

    const updateAria = () => {
      summary.setAttribute("aria-expanded", card.open ? "true" : "false");
    };

    updateAria();
    if (!card.dataset.ariaAttached) {
      card.dataset.ariaAttached = "true";
      card.addEventListener("toggle", updateAria);
    }
  };

  const setupCorrectionAnchorScroll = () => {
    const hash = window.location.hash;
    const urlParams = new URLSearchParams(window.location.search);
    const focusTarget = urlParams.get("focus");

    let targetElement = null;
    if (hash) {
      try {
        targetElement = document.querySelector(hash);
      } catch (_e) {
        targetElement = null;
      }
    }
    if (!targetElement && focusTarget) {
      if (focusTarget === "materials") {
        targetElement = document.getElementById("material-section");
      } else if (focusTarget === "choices") {
        targetElement = document.getElementById("choice-section");
      } else if (focusTarget === "classification") {
        targetElement = document.getElementById("classification-section");
      }
    }

    if (targetElement) {
      if (targetElement.tagName === "DETAILS" && !targetElement.open) {
        targetElement.open = true;
      }
      setTimeout(() => {
        targetElement.scrollIntoView({ behavior: "smooth", block: "start" });
        targetElement.classList.add("assistant-section--highlighted");
        const firstInput = targetElement.querySelector("input:not([type=hidden]), select, textarea, button");
        firstInput?.focus();
        setTimeout(() => {
          targetElement.classList.remove("assistant-section--highlighted");
        }, 2000);
      }, 100);
    }
  };

  document.body.addEventListener("htmx:beforeRequest", (event) => {
    const control = workspaceControl(event);
    if (control) {
      pendingControlId = control.id;
      hideTransportRecovery();
      setWorkspaceActionBusy(control, true);
      currentResults()?.setAttribute("aria-busy", "true");
      return;
    }

    const replyControl = readyReplyControl(event);
    if (replyControl) {
      hideReadyReplyTransportRecovery(replyControl);
      return;
    }

    const formControl = productFormControl(event);
    if (formControl) {
      hideProductFormTransportRecovery();
      setProductFormBusy(formControl, true);
    }
  });

  document.body.addEventListener("htmx:afterSwap", (event) => {
    const target = event.detail?.target;
    syncFieldErrors(target || document);
    setupInstantMediaPreview(target || document);
    syncVocabularyCardAccessibility(target || document);

    const formControl = productFormControl(event);
    if (formControl) {
      setProductFormBusy(formControl, false);
    }
    if (target?.matches?.("[data-ready-reply-slot]") || target?.id === "ready-reply-root") {
      const root = target.querySelector("[data-ready-reply-root]") || (target.matches("[data-ready-reply-root]") ? target : null);
      const triggerId = root?.dataset.readyReplyTriggerId || target.dataset.readyReplyTriggerId;
      const trigger = triggerId ? document.getElementById(triggerId) : null;
      const panel = target.querySelector("[data-ready-reply-panel]");
      if (!panel) {
        showReadyReplyTransportRecovery(trigger);
        return;
      }
      trigger?.setAttribute("aria-expanded", "true");
      panel.focus();
      return;
    }

    if (target?.id !== "product-workspace-results") {
      return;
    }

    syncDeckState(target);

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
    const replyControl = readyReplyControl(event);
    if (replyControl && event.detail?.successful === false) {
      showReadyReplyTransportRecovery(replyControl);
    }
    const formControl = productFormControl(event);
    if (formControl && event.detail?.successful === false) {
      showProductFormTransportRecovery(formControl);
    }
  });

  for (const eventName of ["htmx:sendError", "htmx:timeout", "htmx:swapError"]) {
    document.body.addEventListener(eventName, (event) => {
      if (workspaceControl(event)) {
        showTransportRecovery();
      }
      const replyControl = readyReplyControl(event);
      if (replyControl) {
        showReadyReplyTransportRecovery(replyControl);
      }
      const formControl = productFormControl(event);
      if (formControl) {
        showProductFormTransportRecovery(formControl);
      }
    });
  }

  document.body.addEventListener("click", async (event) => {
    const deckToggle = event.target.closest?.("[data-deck-toggle]");
    if (deckToggle) {
      toggleDeck(deckToggle);
      return;
    }

    if (!event.target.closest("[data-overflow-menu]")) {
      for (const openOverflow of document.querySelectorAll(
        "[data-overflow-menu][open]",
      )) {
        openOverflow.removeAttribute("open");
      }
    }

    const backdrop = event.target.closest?.("[data-ready-reply-backdrop]");
    if (backdrop) {
      closeReadyReply(backdrop);
      return;
    }

    const closeButton = event.target.closest?.("[data-ready-reply-close]");
    if (closeButton) {
      closeReadyReply(closeButton);
      return;
    }

    const copyButton = event.target.closest?.("[data-ready-reply-copy]");
    if (!copyButton) {
      return;
    }
    const panel = copyButton.closest("[data-ready-reply-panel]");
    const copyText = document.getElementById(
      copyButton.dataset.readyReplyCopyTarget,
    );
    const status = panel?.querySelector("[data-ready-reply-copy-status]");
    if (!copyText || !status) {
      return;
    }

    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error("Clipboard API unavailable");
      }
      await navigator.clipboard.writeText(copyText.value);
      status.setAttribute("role", "status");
      status.textContent = "პასუხი დაკოპირებულია.";
      status.hidden = false;
      setTimeout(() => {
        closeReadyReply(panel);
      }, 250);
    } catch (_error) {
      status.setAttribute("role", "alert");
      status.textContent = "დაკოპირება ვერ მოხერხდა. მონიშნეთ ტექსტი და ხელით დააკოპირეთ.";
      status.hidden = false;
      copyText.focus();
      copyText.select();
    }
  });

  document.body.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
      return;
    }
    const openOverflow = document.activeElement?.closest?.(
      "[data-overflow-menu][open]",
    );
    if (openOverflow) {
      event.preventDefault();
      openOverflow.removeAttribute("open");
      openOverflow.querySelector("summary")?.focus();
      return;
    }
    const openReadyReply = document.querySelector("[data-ready-reply-root]");
    if (openReadyReply) {
      event.preventDefault();
      closeReadyReply(openReadyReply);
      return;
    }
  });

  syncWorkspaceFormAccessibility();
  syncFieldErrors();
  syncDeckState();
  setupInstantMediaPreview();
  syncVocabularyCardAccessibility();
  setupCorrectionAnchorScroll();
})();
