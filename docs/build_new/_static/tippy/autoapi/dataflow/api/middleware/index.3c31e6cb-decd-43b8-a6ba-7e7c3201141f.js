selector_to_html = {"a[href=\"rate_limit/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.middleware.rate_limit<a class=\"headerlink\" href=\"#module-dataflow.api.middleware.rate_limit\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-dataflow.api.middleware\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.middleware<a class=\"headerlink\" href=\"#module-dataflow.api.middleware\" title=\"Link to this heading\">\u00b6</a></h1><p>Middleware - TODO: Add brief description.</p><p>TODO: Add detailed description of module functionality</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"logging/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.middleware.logging<a class=\"headerlink\" href=\"#module-dataflow.api.middleware.logging\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"supabase_logging/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.middleware.supabase_logging<a class=\"headerlink\" href=\"#module-dataflow.api.middleware.supabase_logging\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"auth/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.middleware.auth<a class=\"headerlink\" href=\"#module-dataflow.api.middleware.auth\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
