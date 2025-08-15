selector_to_html = {"a[href=\"environment/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.config.environment<a class=\"headerlink\" href=\"#module-dataflow.config.environment\" title=\"Link to this heading\">\u00b6</a></h1><h2>Classes<a class=\"headerlink\" href=\"#classes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-dataflow.config\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.config<a class=\"headerlink\" href=\"#module-dataflow.config\" title=\"Link to this heading\">\u00b6</a></h1><p>Config - TODO: Add brief description.</p><p>TODO: Add detailed description of module functionality</p>", "a[href=\"settings/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.config.settings<a class=\"headerlink\" href=\"#module-dataflow.config.settings\" title=\"Link to this heading\">\u00b6</a></h1><p>Application settings configuration for the Haive framework.</p><p>This module defines Pydantic models for application settings, providing\na type-safe and validated configuration system. Settings are automatically\nloaded from environment variables with sensible defaults.</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>"}
skip_classes = ["headerlink", "sd-stretched-link"]

window.onload = function () {
    for (const [select, tip_html] of Object.entries(selector_to_html)) {
        const links = document.querySelectorAll(`article.bd-article ${select}`);
        for (const link of links) {
            if (skip_classes.some(c => link.classList.contains(c))) {
                continue;
            }
            link.classList.add('has-tooltip');
            tippy(link, {
                content: tip_html,
                allowHTML: true,
                arrow: true,
                placement: 'auto-start', maxWidth: 600, interactive: true, theme: 'light-border', delay: [200, 100], duration: [200, 100],
                onShow(instance) {MathJax.typesetPromise([instance.popper]).then(() => {});},
            });
        };
    };
    console.log("tippy tips loaded!");
};
