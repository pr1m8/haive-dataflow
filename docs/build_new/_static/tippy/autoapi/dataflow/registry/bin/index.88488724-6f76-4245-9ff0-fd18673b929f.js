selector_to_html = {"a[href=\"litellm_cli/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.registry.bin.litellm_cli<a class=\"headerlink\" href=\"#module-dataflow.registry.bin.litellm_cli\" title=\"Link to this heading\">\u00b6</a></h1><p>Haive Vault CLI.</p><p>A command-line utility for managing vault secrets and model imports.</p>", "a[href=\"#module-dataflow.registry.bin\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.registry.bin<a class=\"headerlink\" href=\"#module-dataflow.registry.bin\" title=\"Link to this heading\">\u00b6</a></h1><p>Bin module.</p><p>This module is part of the Haive framework.\nLocation: haive-dataflow/src/haive/dataflow/registry/bin</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"registry_cli/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.registry.bin.registry_cli<a class=\"headerlink\" href=\"#module-dataflow.registry.bin.registry_cli\" title=\"Link to this heading\">\u00b6</a></h1><p>Haive Registry CLI.</p><p>This script provides a command-line interface for the Haive registry system.\nIt allows users to:\n- Discover and register components (agents, tools, engines, games, etc.)\n- View registry statistics\n- Import LLM models\n- Search for components\n- View detailed information about components</p>", "a[href=\"vault_cli/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.registry.bin.vault_cli<a class=\"headerlink\" href=\"#module-dataflow.registry.bin.vault_cli\" title=\"Link to this heading\">\u00b6</a></h1><p>Fixed Vault CLI.</p><p>A command-line utility to manage vault secrets and model imports, with\nproper schema mapping for Supabase.</p>"}
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
