selector_to_html = {"a[href=\"#recent-documentation-updates\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Recent Documentation Updates<a class=\"headerlink\" href=\"#recent-documentation-updates\" title=\"Link to this heading\">\u00b6</a></h2><p><strong>How to Use This Page:</strong></p>", "a[href=\"#release-notes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Release Notes<a class=\"headerlink\" href=\"#release-notes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#changelog\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">Changelog<a class=\"headerlink\" href=\"#changelog\" title=\"Link to this heading\">\u00b6</a></h1><p>This page tracks changes to haive-dataflow using both manual entries and Git history.</p>"}
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
