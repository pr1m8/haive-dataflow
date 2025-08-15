selector_to_html = {"a[href=\"#dataflow.registry.main.agents\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registry.main.agents\">\n<span class=\"sig-name descname\"><span class=\"pre\">agents</span></span></dt><dd></dd>", "a[href=\"#dataflow.registry.main.agent_ids\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registry.main.agent_ids\">\n<span class=\"sig-name descname\"><span class=\"pre\">agent_ids</span></span></dt><dd></dd>", "a[href=\"#dataflow.registry.main.import_logs\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registry.main.import_logs\">\n<span class=\"sig-name descname\"><span class=\"pre\">import_logs</span></span></dt><dd></dd>", "a[href=\"#module-dataflow.registry.main\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.registry.main<a class=\"headerlink\" href=\"#module-dataflow.registry.main\" title=\"Link to this heading\">\u00b6</a></h1><h2>Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#dataflow.registry.main.session_id\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registry.main.session_id\">\n<span class=\"sig-name descname\"><span class=\"pre\">session_id</span></span><em class=\"property\"><span class=\"w\"> </span><span class=\"p\"><span class=\"pre\">=</span></span><span class=\"w\"> </span><span class=\"pre\">''</span></em></dt><dd></dd>", "a[href=\"#dataflow.registry.main.deps\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registry.main.deps\">\n<span class=\"sig-name descname\"><span class=\"pre\">deps</span></span></dt><dd></dd>", "a[href=\"#attributes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-contents\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Module Contents<a class=\"headerlink\" href=\"#module-contents\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
