selector_to_html = {"a[href=\"#dataflow.main.console\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.main.console\">\n<span class=\"sig-name descname\"><span class=\"pre\">console</span></span></dt><dd></dd>", "a[href=\"#dataflow.main.LOG_LEVEL\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.main.LOG_LEVEL\">\n<span class=\"sig-name descname\"><span class=\"pre\">LOG_LEVEL</span></span></dt><dd></dd>", "a[href=\"#dataflow.main.settings\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.main.settings\">\n<span class=\"sig-name descname\"><span class=\"pre\">settings</span></span></dt><dd></dd>", "a[href=\"#dataflow.main.display_startup_info\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.main.display_startup_info\">\n<span class=\"sig-name descname\"><span class=\"pre\">display_startup_info</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span></dt><dd><p>Display rich startup information.</p></dd>", "a[href=\"#dataflow.main.main\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.main.main\">\n<span class=\"sig-name descname\"><span class=\"pre\">main</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span></dt><dd><p>Run the application server.</p></dd>", "a[href=\"#dataflow.main.logger\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.main.logger\">\n<span class=\"sig-name descname\"><span class=\"pre\">logger</span></span></dt><dd></dd>", "a[href=\"#module-dataflow.main\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.main<a class=\"headerlink\" href=\"#module-dataflow.main\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#functions\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Functions<a class=\"headerlink\" href=\"#functions\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#attributes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-contents\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Module Contents<a class=\"headerlink\" href=\"#module-contents\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
