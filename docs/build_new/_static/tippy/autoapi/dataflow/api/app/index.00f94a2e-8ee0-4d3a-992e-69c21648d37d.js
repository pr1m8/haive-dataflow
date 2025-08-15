selector_to_html = {"a[href=\"#dataflow.api.app.create_app\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.app.create_app\">\n<span class=\"sig-name descname\"><span class=\"pre\">create_app</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span> <span class=\"sig-return\"><span class=\"sig-return-icon\">\u2192</span> <span class=\"sig-return-typehint\"><a class=\"reference external\" href=\"https://fastapi.tiangolo.com/reference/fastapi/#fastapi.FastAPI\" title=\"(in FastAPI v0.0.0)\"><span class=\"pre\">fastapi.FastAPI</span></a></span></span></dt><dd><p>Create and configure the FastAPI application.</p><p>This function creates a new FastAPI application instance, configures middleware\nfor CORS, authentication, logging, and rate limiting, and registers the API\nroutes for agents, conversations, LLM models, and game agents.</p><p>The application configuration is loaded from settings, allowing for\nenvironment-specific customization.</p><p class=\"rubric\">Example</p></dd>", "a[href=\"#module-contents\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Module Contents<a class=\"headerlink\" href=\"#module-contents\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-dataflow.api.app\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.app<a class=\"headerlink\" href=\"#module-dataflow.api.app\" title=\"Link to this heading\">\u00b6</a></h1><p>Haive API Application Module.</p><p>This module defines and configures the FastAPI application for the Haive framework.\nIt sets up middleware, routes, and the core API functionality.</p>", "a[href=\"#dataflow.api.app.logger\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.app.logger\">\n<span class=\"sig-name descname\"><span class=\"pre\">logger</span></span></dt><dd></dd>", "a[href=\"#dataflow.api.app.validation_exception_handler\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.app.validation_exception_handler\">\n<em class=\"property\"><span class=\"k\"><span class=\"pre\">async</span></span><span class=\"w\"> </span></em><span class=\"sig-name descname\"><span class=\"pre\">validation_exception_handler</span></span><span class=\"sig-paren\">(</span><em class=\"sig-param\"><span class=\"n\"><span class=\"pre\">request</span></span></em>, <em class=\"sig-param\"><span class=\"n\"><span class=\"pre\">exc</span></span></em><span class=\"sig-paren\">)</span></dt><dd></dd>", "a[href=\"#dataflow.api.app.settings\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.app.settings\">\n<span class=\"sig-name descname\"><span class=\"pre\">settings</span></span></dt><dd></dd>", "a[href=\"#dataflow.api.app.app\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.app.app\">\n<span class=\"sig-name descname\"><span class=\"pre\">app</span></span></dt><dd></dd>", "a[href=\"#functions\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Functions<a class=\"headerlink\" href=\"#functions\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#id0\"]": "<dt class=\"sig sig-object py\" id=\"id0\">\n<span class=\"sig-name descname\"><span class=\"pre\">logger</span></span></dt><dd></dd>", "a[href=\"#attributes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
