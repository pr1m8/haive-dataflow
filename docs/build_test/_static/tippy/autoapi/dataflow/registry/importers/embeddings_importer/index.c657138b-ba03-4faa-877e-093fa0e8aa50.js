selector_to_html = {"a[href=\"#module-contents\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Module Contents<a class=\"headerlink\" href=\"#module-contents\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-dataflow.registry.importers.embeddings_importer\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.registry.importers.embeddings_importer<a class=\"headerlink\" href=\"#module-dataflow.registry.importers.embeddings_importer\" title=\"Link to this heading\">\u00b6</a></h1><p>Embedding Models Importer for the Haive Registry System.</p><p>This module provides functionality for importing embedding models from\nvarious providers and registering them in the system.</p>", "a[href=\"#dataflow.registry.importers.embeddings_importer.EMBEDDING_MODELS\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registry.importers.embeddings_importer.EMBEDDING_MODELS\">\n<span class=\"sig-name descname\"><span class=\"pre\">EMBEDDING_MODELS</span></span></dt><dd></dd>", "a[href=\"#dataflow.registry.importers.embeddings_importer.logger\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registry.importers.embeddings_importer.logger\">\n<span class=\"sig-name descname\"><span class=\"pre\">logger</span></span></dt><dd></dd>", "a[href=\"#functions\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Functions<a class=\"headerlink\" href=\"#functions\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#attributes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#dataflow.registry.importers.embeddings_importer.import_embedding_models\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.registry.importers.embeddings_importer.import_embedding_models\">\n<span class=\"sig-name descname\"><span class=\"pre\">import_embedding_models</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span> <span class=\"sig-return\"><span class=\"sig-return-icon\">\u2192</span> <span class=\"sig-return-typehint\"><a class=\"reference external\" href=\"https://docs.python.org/3/library/functions.html#bool\" title=\"(in Python v3.13)\"><span class=\"pre\">bool</span></a></span></span></dt><dd><p>Import embedding models into the registry.</p></dd>"}
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
