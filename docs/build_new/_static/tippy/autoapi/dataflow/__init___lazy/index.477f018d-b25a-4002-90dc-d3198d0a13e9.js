selector_to_html = {"a[href=\"#module-dataflow.__init___lazy\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.__init___lazy<a class=\"headerlink\" href=\"#module-dataflow.__init___lazy\" title=\"Link to this heading\">\u00b6</a></h1><p>Haive Dataflow - Registry and Discovery System (Lazy Loading).</p><p>This is a lazy-loading version of the haive-dataflow package that prevents\nheavy initialization at import time. The registry system and database\nconnections are only initialized when actually needed.</p>"}
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
