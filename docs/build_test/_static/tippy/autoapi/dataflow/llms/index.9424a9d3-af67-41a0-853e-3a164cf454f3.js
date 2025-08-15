selector_to_html = {"a[href=\"#module-dataflow.llms\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.llms<a class=\"headerlink\" href=\"#module-dataflow.llms\" title=\"Link to this heading\">\u00b6</a></h1><p>Llms - TODO: Add brief description.</p><p>TODO: Add detailed description of module functionality</p>", "a[href=\"models/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.llms.models<a class=\"headerlink\" href=\"#module-dataflow.llms.models\" title=\"Link to this heading\">\u00b6</a></h1><p>LLM Provider and Model Data Models.</p><p>This module defines Pydantic models for representing LLM providers, models,\nand their capabilities within the Haive dataflow system. These models are\nused for provider registration, capability tracking, and cost management.</p>", "a[href=\"api/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.llms.api<a class=\"headerlink\" href=\"#module-dataflow.llms.api\" title=\"Link to this heading\">\u00b6</a></h1><p>API endpoints for LLM model information and availability.</p><p>This module provides FastAPI endpoints to access and manage LLM model\ndata stored in Supabase. It helps bridge the client application with the\ndatabase while providing additional server-side logic.</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
