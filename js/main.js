(function () {
  "use strict";

  // mobile nav toggle
  const header = document.querySelector(".site-header");
  const toggle = document.querySelector(".nav-toggle");
  if (header && toggle) {
    toggle.addEventListener("click", () => {
      header.classList.toggle("nav-mobile-open");
      const open = header.classList.contains("nav-mobile-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    document.querySelectorAll(".nav-links a").forEach((a) => {
      a.addEventListener("click", () => {
        header.classList.remove("nav-mobile-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // scroll reveal
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("sr-in");
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    document.querySelectorAll("[data-sr]").forEach((el) => observer.observe(el));
  } else {
    document.querySelectorAll("[data-sr]").forEach((el) => el.classList.add("sr-in"));
  }

  // marquee duplication for seamless loop
  document.querySelectorAll(".marquee-track").forEach((track) => {
    const clone = track.cloneNode(true);
    clone.setAttribute("aria-hidden", "true");
    track.parentNode.appendChild(clone);
  });

  // contact form
  const form = document.querySelector("[data-contact-form]");
  if (form) {
    const status = form.querySelector(".form-status");
    const submitBtn = form.querySelector('button[type="submit"]');
    const submitLabel = submitBtn ? submitBtn.textContent : "";

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      status.className = "form-status";
      status.textContent = "";

      const consent = form.querySelector('input[name="consent_transactional"]');
      if (consent && !consent.checked) {
        status.classList.add("is-error");
        status.textContent = "Please confirm consent to receive transactional messages so we can follow up.";
        return;
      }

      const data = Object.fromEntries(new FormData(form).entries());
      data.source = "achievers-wealth-academy";
      data.page = window.location.pathname;
      data.submitted_at = new Date().toISOString();

      const endpoint = form.dataset.endpoint;

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Sending…";
      }

      try {
        if (endpoint && endpoint.startsWith("http")) {
          const res = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
          });
          if (!res.ok) throw new Error("Webhook returned " + res.status);
        } else {
          await new Promise((r) => setTimeout(r, 600));
        }
        status.classList.add("is-success");
        status.textContent = "Thanks, " + (data.first_name || "we got your details") + ". A member of our team will reach out within one business day.";
        form.reset();
      } catch (err) {
        status.classList.add("is-error");
        status.textContent = "Something went wrong sending your message. Please call (201) 912-1781 or email cherryjaneokeke@gmail.com directly.";
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = submitLabel;
        }
      }
    });
  }

  // year stamp
  document.querySelectorAll("[data-year]").forEach((el) => {
    el.textContent = new Date().getFullYear();
  });
})();
