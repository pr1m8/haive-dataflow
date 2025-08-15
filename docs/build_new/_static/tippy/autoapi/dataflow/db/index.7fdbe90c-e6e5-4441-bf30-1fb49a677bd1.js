selector_to_html = {"a[href=\"#module-dataflow.db\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.db<a class=\"headerlink\" href=\"#module-dataflow.db\" title=\"Link to this heading\">\u00b6</a></h1><p>Db - TODO: Add brief description.</p><p>TODO: Add detailed description of module functionality</p>", "a[href=\"schema/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.db.schema<a class=\"headerlink\" href=\"#module-dataflow.db.schema\" title=\"Link to this heading\">\u00b6</a></h1><p>Database schema management for the Haive Registry System.</p><p>This module provides functions for creating and managing the database\nschema for the registry system. It handles schema creation, migrations,\nand upgrades as needed.</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"supabase/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.db.supabase<a class=\"headerlink\" href=\"#module-dataflow.db.supabase\" title=\"Link to this heading\">\u00b6</a></h1><p>Supabase database integration for the Haive registry system.</p><p>This module provides functionality for connecting to and interacting with a\nSupabase database instance for storing registry data. It handles connection\nmanagement, schema mapping, and query execution.</p>", "a[href=\"inspect_supabase/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.db.inspect_supabase<a class=\"headerlink\" href=\"#module-dataflow.db.inspect_supabase\" title=\"Link to this heading\">\u00b6</a></h1><h2>Functions<a class=\"headerlink\" href=\"#functions\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
