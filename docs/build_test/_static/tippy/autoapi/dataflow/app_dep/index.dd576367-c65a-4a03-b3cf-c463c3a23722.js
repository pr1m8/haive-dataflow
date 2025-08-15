selector_to_html = {"a[href=\"#dataflow.app_dep.logger\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.app_dep.logger\">\n<span class=\"sig-name descname\"><span class=\"pre\">logger</span></span></dt><dd></dd>", "a[href=\"#dataflow.app_dep.app\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.app_dep.app\">\n<span class=\"sig-name descname\"><span class=\"pre\">app</span></span></dt><dd></dd>", "a[href=\"#module-dataflow.app_dep\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.app_dep<a class=\"headerlink\" href=\"#module-dataflow.app_dep\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#functions\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Functions<a class=\"headerlink\" href=\"#functions\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#dataflow.app_dep.create_app\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.app_dep.create_app\">\n<span class=\"sig-name descname\"><span class=\"pre\">create_app</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span> <span class=\"sig-return\"><span class=\"sig-return-icon\">\u2192</span> <span class=\"sig-return-typehint\"><a class=\"reference external\" href=\"https://fastapi.tiangolo.com/reference/fastapi/#fastapi.FastAPI\" title=\"(in FastAPI v0.0.0)\"><span class=\"pre\">fastapi.FastAPI</span></a></span></span></dt><dd><p>Create the FastAPI application.</p></dd>", "a[href=\"#attributes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-contents\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Module Contents<a class=\"headerlink\" href=\"#module-contents\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
