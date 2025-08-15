selector_to_html = {"a[href=\"#module-dataflow.internal_websockets\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.internal_websockets<a class=\"headerlink\" href=\"#module-dataflow.internal_websockets\" title=\"Link to this heading\">\u00b6</a></h1><p>Internal Websockets - TODO: Add brief description.</p><p>TODO: Add detailed description of module functionality</p>", "a[href=\"handlers/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.internal_websockets.handlers<a class=\"headerlink\" href=\"#module-dataflow.internal_websockets.handlers\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"manager/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.internal_websockets.manager<a class=\"headerlink\" href=\"#module-dataflow.internal_websockets.manager\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
