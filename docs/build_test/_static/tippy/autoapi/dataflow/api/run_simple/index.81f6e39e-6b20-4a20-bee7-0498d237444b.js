selector_to_html = {"a[href=\"#dataflow.api.run_simple.current_dir\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_simple.current_dir\">\n<span class=\"sig-name descname\"><span class=\"pre\">current_dir</span></span></dt><dd></dd>", "a[href=\"#module-dataflow.api.run_simple\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.run_simple<a class=\"headerlink\" href=\"#module-dataflow.api.run_simple\" title=\"Link to this heading\">\u00b6</a></h1><p>Simple standalone script to run the Haive Game API.</p><p>This script runs the game router directly without depending on other\nHaive modules. It\u2019s designed for testing the game router functionality\nin isolation.</p>", "a[href=\"#dataflow.api.run_simple.logger\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_simple.logger\">\n<span class=\"sig-name descname\"><span class=\"pre\">logger</span></span></dt><dd></dd>", "a[href=\"#dataflow.api.run_simple.main\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_simple.main\">\n<span class=\"sig-name descname\"><span class=\"pre\">main</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span></dt><dd><p>Run the API server.</p></dd>", "a[href=\"#functions\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Functions<a class=\"headerlink\" href=\"#functions\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#attributes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-contents\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Module Contents<a class=\"headerlink\" href=\"#module-contents\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
