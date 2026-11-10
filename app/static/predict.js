document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("predict-form");
    const button = document.getElementById("submit-button");

    if (!form || !button) {
        return;
    }

    form.addEventListener("submit", function () {

        if (!form.checkValidity()) {
            return;
        }

        button.disabled = true;
        button.textContent = "Memproses...";

    });

});