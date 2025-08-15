selector_to_html = {"a[href=\"health/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.mcp.health<a class=\"headerlink\" href=\"#module-dataflow.mcp.health\" title=\"Link to this heading\">\u00b6</a></h1><p>MCP Health Monitoring for haive-dataflow.</p><p>This module provides health monitoring and management capabilities for MCP servers,\nincluding connection status tracking, performance metrics, and automatic recovery.</p>", "a[href=\"#module-dataflow.mcp\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.mcp<a class=\"headerlink\" href=\"#module-dataflow.mcp\" title=\"Link to this heading\">\u00b6</a></h1><p>MCP (Model Context Protocol) integration for haive-dataflow.</p><p>This module provides comprehensive MCP server discovery, management, and integration\nwith the Haive framework through the dataflow registry system.</p>", "a[href=\"client/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.mcp.client<a class=\"headerlink\" href=\"#module-dataflow.mcp.client\" title=\"Link to this heading\">\u00b6</a></h1><p>MCP Client Integration for haive-dataflow.</p><p>This module provides integration between MCP servers and the Haive framework\nthrough LangChain MCP adapters and the dataflow registry system.</p>", "a[href=\"#submodules\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Submodules<a class=\"headerlink\" href=\"#submodules\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"discovery/index.html\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.mcp.discovery<a class=\"headerlink\" href=\"#module-dataflow.mcp.discovery\" title=\"Link to this heading\">\u00b6</a></h1><p>MCP Server Discovery for haive-dataflow.</p><p>This module provides discovery capabilities for MCP (Model Context Protocol) servers\nfrom various sources and integrates them with the haive-dataflow registry system.</p>"}
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
