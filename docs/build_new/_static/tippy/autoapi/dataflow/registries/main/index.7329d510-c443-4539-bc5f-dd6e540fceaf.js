selector_to_html = {"a[href=\"#module-contents\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Module Contents<a class=\"headerlink\" href=\"#module-contents\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#dataflow.registries.main.ensure_provider_types\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registries.main.ensure_provider_types\">\n<span class=\"sig-name descname\"><span class=\"pre\">ensure_provider_types</span></span><span class=\"sig-paren\">(</span><em class=\"sig-param\"><span class=\"n\"><span class=\"pre\">client</span></span></em><span class=\"sig-paren\">)</span></dt><dd><p>Ensure provider types exist in database.</p></dd>", "a[href=\"#dataflow.registries.main.logger\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registries.main.logger\">\n<span class=\"sig-name descname\"><span class=\"pre\">logger</span></span></dt><dd></dd>", "a[href=\"#module-dataflow.registries.main\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.registries.main<a class=\"headerlink\" href=\"#module-dataflow.registries.main\" title=\"Link to this heading\">\u00b6</a></h1><p>Test script for the LLM and Embedding model registry system.</p>", "a[href=\"#functions\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Functions<a class=\"headerlink\" href=\"#functions\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#dataflow.registries.main.ensure_registry_schema\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registries.main.ensure_registry_schema\">\n<span class=\"sig-name descname\"><span class=\"pre\">ensure_registry_schema</span></span><span class=\"sig-paren\">(</span><em class=\"sig-param\"><span class=\"n\"><span class=\"pre\">client</span></span></em><span class=\"sig-paren\">)</span></dt><dd><p>Ensure the registry schema exists in database.</p></dd>", "a[href=\"#dataflow.registries.main.main\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registries.main.main\">\n<span class=\"sig-name descname\"><span class=\"pre\">main</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span></dt><dd><p>Main test function.</p></dd>", "a[href=\"#attributes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
