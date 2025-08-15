selector_to_html = {"a[href=\"changelog.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">Changelog<a class=\"headerlink\" href=\"#changelog\" title=\"Link to this heading\">\u00b6</a></h1><p>This page tracks changes to haive-dataflow using both manual entries and Git history.</p>", "a[href=\"#indices-and-tables\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">Indices and Tables<a class=\"headerlink\" href=\"#indices-and-tables\" title=\"Link to this heading\">\u00b6</a></h1>", "a[href=\"changelog.html#recent-documentation-updates\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Recent Documentation Updates<a class=\"headerlink\" href=\"#recent-documentation-updates\" title=\"Link to this heading\">\u00b6</a></h2><p><strong>How to Use This Page:</strong></p>", "a[href=\"changelog.html#release-notes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Release Notes<a class=\"headerlink\" href=\"#release-notes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#development\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Development<a class=\"headerlink\" href=\"#development\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#examples\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Examples<a class=\"headerlink\" href=\"#examples\" title=\"Link to this heading\">\u00b6</a></h2><p>Explore practical examples and tutorials:</p>", "a[href=\"#haive-dataflow-documentation\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">Haive Dataflow Documentation<a class=\"headerlink\" href=\"#haive-dataflow-documentation\" title=\"Link to this heading\">\u00b6</a></h1><p>Welcome to <strong>Haive Dataflow</strong> - Data processing pipelines and persistence systems.</p><p>This package is part of the Haive AI Agent Framework ecosystem.</p>", "a[href=\"#command-line-interface\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Command Line Interface<a class=\"headerlink\" href=\"#command-line-interface\" title=\"Link to this heading\">\u00b6</a></h2><p>{config[\u201ctitle\u201d]} provides CLI tools for easy interaction:</p>", "a[href=\"autoapi/dataflow/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow<a class=\"headerlink\" href=\"#module-dataflow\" title=\"Link to this heading\">\u00b6</a></h1><p>Haive Dataflow - Registry and Discovery System (Lazy Loading).</p><p>This is a lazy-loading version of the haive-dataflow package that prevents\nheavy initialization at import time. The registry system and database\nconnections are only initialized when actually needed.</p>", "a[href=\"autoapi/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">API Reference<a class=\"headerlink\" href=\"#api-reference\" title=\"Link to this heading\">\u00b6</a></h1><p>This page contains auto-generated API reference documentation <a class=\"footnote-reference brackets\" href=\"#f1\" id=\"id1\" role=\"doc-noteref\"><span class=\"fn-bracket\">[</span>1<span class=\"fn-bracket\">]</span></a>.</p>", "a[href=\"#api-reference\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">API Reference<a class=\"headerlink\" href=\"#api-reference\" title=\"Link to this heading\">\u00b6</a></h2><p>Complete API documentation for Haive Dataflow:</p>", "a[href=\"#changelog\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Changelog<a class=\"headerlink\" href=\"#changelog\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
