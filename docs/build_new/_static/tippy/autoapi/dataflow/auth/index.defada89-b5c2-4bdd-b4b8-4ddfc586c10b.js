selector_to_html = {"a[href=\"middleware/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.auth.middleware<a class=\"headerlink\" href=\"#module-dataflow.auth.middleware\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"dependencies/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.auth.dependencies<a class=\"headerlink\" href=\"#module-dataflow.auth.dependencies\" title=\"Link to this heading\">\u00b6</a></h1><p>Authentication dependencies for FastAPI routes.</p><p>This module provides FastAPI dependency functions for authentication in the\nHaive API. It includes dependencies for both optional and required authentication,\nsupporting different levels of access control for API endpoints.</p>", "a[href=\"supabase/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.auth.supabase<a class=\"headerlink\" href=\"#module-dataflow.auth.supabase\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"credits/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.auth.credits<a class=\"headerlink\" href=\"#module-dataflow.auth.credits\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-dataflow.auth\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.auth<a class=\"headerlink\" href=\"#module-dataflow.auth\" title=\"Link to this heading\">\u00b6</a></h1><p>Auth - TODO: Add brief description.</p><p>TODO: Add detailed description of module functionality</p>"}
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
