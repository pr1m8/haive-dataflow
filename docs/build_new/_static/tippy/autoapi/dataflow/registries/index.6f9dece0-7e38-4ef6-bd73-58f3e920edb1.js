selector_to_html = {"a[href=\"#module-dataflow.registries\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.registries<a class=\"headerlink\" href=\"#module-dataflow.registries\" title=\"Link to this heading\">\u00b6</a></h1><p>Registries - TODO: Add brief description.</p><p>TODO: Add detailed description of module functionality</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"main/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.registries.main<a class=\"headerlink\" href=\"#module-dataflow.registries.main\" title=\"Link to this heading\">\u00b6</a></h1><p>Test script for the LLM and Embedding model registry system.</p>", "a[href=\"model_registry/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.registries.model_registry<a class=\"headerlink\" href=\"#module-dataflow.registries.model_registry\" title=\"Link to this heading\">\u00b6</a></h1><p>Model Registry Client for Haive.</p><p>This module provides a client interface for working with the registry\nsystem to access LLM and embedding models with dynamic environment\nvariable detection.</p>"}
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
