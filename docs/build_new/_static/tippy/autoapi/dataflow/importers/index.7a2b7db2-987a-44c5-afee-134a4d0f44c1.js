selector_to_html = {"a[href=\"#module-dataflow.importers\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.importers<a class=\"headerlink\" href=\"#module-dataflow.importers\" title=\"Link to this heading\">\u00b6</a></h1><p>Importers for the Haive Registry System.</p><p>This package provides importers for external data sources, allowing the\nregistry to import models, providers, and other components from external\nsystems.</p>", "a[href=\"litellm_importer/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.importers.litellm_importer<a class=\"headerlink\" href=\"#module-dataflow.importers.litellm_importer\" title=\"Link to this heading\">\u00b6</a></h1><p>Fixed LiteLLM Importer Module.</p><p>This module imports LLM and embedding models from LiteLLM data and other\nsources into Supabase, properly handling all models without limits.</p>", "a[href=\"tak/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.importers.tak<a class=\"headerlink\" href=\"#module-dataflow.importers.tak\" title=\"Link to this heading\">\u00b6</a></h1><p>Hybrid Tools and Toolkits Importer.</p><p>This script first identifies tools using your working approach, then\nimports them to the database.</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"embeddings_importer/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.importers.embeddings_importer<a class=\"headerlink\" href=\"#module-dataflow.importers.embeddings_importer\" title=\"Link to this heading\">\u00b6</a></h1><p>Embedding Models Importer for the Haive Registry System.</p><p>This module provides functionality for importing embedding models from\nvarious providers and registering them in the system.</p>"}
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
