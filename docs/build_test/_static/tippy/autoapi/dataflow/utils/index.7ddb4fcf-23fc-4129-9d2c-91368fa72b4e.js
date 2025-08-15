selector_to_html = {"a[href=\"#module-dataflow.utils\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.utils<a class=\"headerlink\" href=\"#module-dataflow.utils\" title=\"Link to this heading\">\u00b6</a></h1><p>Utilities for the Haive Registry System.</p><p>This package provides utility functions and helpers for the registry\nsystem, including logging utilities and other common functionality.</p>", "a[href=\"vault_migration_script/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.utils.vault_migration_script<a class=\"headerlink\" href=\"#module-dataflow.utils.vault_migration_script\" title=\"Link to this heading\">\u00b6</a></h1><p>Fixed Vault Reference Migration Script.</p><p>This script migrates API keys and secrets to the vault schema, using\nproper schema mapping with the existing table() helper function.</p>", "a[href=\"logging/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.utils.logging<a class=\"headerlink\" href=\"#module-dataflow.utils.logging\" title=\"Link to this heading\">\u00b6</a></h1><p>Logging utilities for the Haive Registry System.</p><p>This module provides logging utilities for the registry system,\nincluding setup functions for various log types.</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
