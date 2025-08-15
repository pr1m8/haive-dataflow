selector_to_html = {"a[href=\"#module-dataflow.providers\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.providers<a class=\"headerlink\" href=\"#module-dataflow.providers\" title=\"Link to this heading\">\u00b6</a></h1><p>Providers - TODO: Add brief description.</p><p>TODO: Add detailed description of module functionality</p>", "a[href=\"base/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.providers.base<a class=\"headerlink\" href=\"#module-dataflow.providers.base\" title=\"Link to this heading\">\u00b6</a></h1><p>Base provider class for the Haive Registry System.</p><p>This module defines the base provider class that all specific entity\nproviders inherit from.</p>", "a[href=\"agent_provider/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.providers.agent_provider<a class=\"headerlink\" href=\"#module-dataflow.providers.agent_provider\" title=\"Link to this heading\">\u00b6</a></h1><p>Agent provider for the Haive Registry System.</p><p>This module implements the agent provider that handles discovery and\nregistration of agent components.</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
