selector_to_html = {"a[href=\"games/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.routers.games<a class=\"headerlink\" href=\"#module-dataflow.api.routers.games\" title=\"Link to this heading\">\u00b6</a></h1><p>Games router for the Haive API.</p><p>This module provides API routes for the general games system,\nintegrating with the haive-games package.</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-dataflow.api.routers\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.routers<a class=\"headerlink\" href=\"#module-dataflow.api.routers\" title=\"Link to this heading\">\u00b6</a></h1><p>Routers module.</p><p>This module is part of the Haive framework.\nLocation: haive-dataflow/src/haive/dataflow/api/routers</p>"}
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
