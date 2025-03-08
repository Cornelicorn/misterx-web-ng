function updateTheme() {
    let saved_theme
    let theme
    let icon
    saved_theme = localStorage.getItem("misterx_theme");
    if (saved_theme == "light") {
        icon = "ti ti-sun";
        theme = "light";
    } else if (saved_theme == "dark") {
        icon = "ti ti-moon";
        theme = "dark"
    } else {
        icon = "ti ti-sun-moon";
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            theme = "dark";
        }
    }
    if (document.getElementById("id_theme_icon")) {
        document.getElementById("id_theme_icon").className = icon;
    }
    if (document.getElementById("id_theme_icon_mobile")) {
        document.getElementById("id_theme_icon_mobile").className = icon;
    }
    document.body.setAttribute("data-bs-theme", theme);
}

function setTheme(mode) {
    localStorage.setItem("misterx_theme", mode);
    updateTheme();
}

updateTheme();

