selector_to_html = {"a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"lite_llm_import/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.fetchers.lite_llm_import<a class=\"headerlink\" href=\"#module-dataflow.fetchers.lite_llm_import\" title=\"Link to this heading\">\u00b6</a></h1><p>LiteLLM Importer for the Haive Registry System.</p><p>This module provides functionality for importing LLM models and\nproviders from LiteLLM\u2019s published model list.</p>", "a[href=\"#module-dataflow.fetchers\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.fetchers<a class=\"headerlink\" href=\"#module-dataflow.fetchers\" title=\"Link to this heading\">\u00b6</a></h1><p>Fetchers - TODO: Add brief description.</p><p>TODO: Add detailed description of module functionality</p>"}
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
