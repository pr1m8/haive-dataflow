selector_to_html = {"a[href=\"conversations/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.persistence.conversations<a class=\"headerlink\" href=\"#module-dataflow.persistence.conversations\" title=\"Link to this heading\">\u00b6</a></h1><p>Conversation persistence for the Haive framework.</p><p>This module provides functionality for persisting and retrieving conversations\nbetween users and agents. It includes classes for managing conversation metadata,\nmessages, and the overall conversation lifecycle.</p>", "a[href=\"#module-dataflow.persistence\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.persistence<a class=\"headerlink\" href=\"#module-dataflow.persistence\" title=\"Link to this heading\">\u00b6</a></h1><p>Persistence - TODO: Add brief description.</p><p>TODO: Add detailed description of module functionality</p>", "a[href=\"supabase_adapter/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.persistence.supabase_adapter<a class=\"headerlink\" href=\"#module-dataflow.persistence.supabase_adapter\" title=\"Link to this heading\">\u00b6</a></h1><p>Supabase persistence adapter for the Haive framework.</p><p>This module provides an adapter for persisting data to Supabase\u2019s PostgreSQL\ndatabase. It handles the connection management, Row-Level Security (RLS)\ncontext, and provides methods for storing and retrieving data.</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
