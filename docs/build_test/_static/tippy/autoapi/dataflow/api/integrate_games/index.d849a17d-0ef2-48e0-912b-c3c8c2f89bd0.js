selector_to_html = {"a[href=\"#dataflow.api.integrate_games.logger\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.integrate_games.logger\">\n<span class=\"sig-name descname\"><span class=\"pre\">logger</span></span></dt><dd></dd>", "a[href=\"#module-dataflow.api.integrate_games\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.integrate_games<a class=\"headerlink\" href=\"#module-dataflow.api.integrate_games\" title=\"Link to this heading\">\u00b6</a></h1><p>Integration module for adding game routes to the main Haive API.</p><p>This module provides functions to add game WebSocket endpoints and routes\nto an existing FastAPI application. It integrates with the game_router module\nto discover and register game agents dynamically.</p>", "a[href=\"#functions\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Functions<a class=\"headerlink\" href=\"#functions\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#dataflow.api.integrate_games.configure_import_paths\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.integrate_games.configure_import_paths\">\n<span class=\"sig-name descname\"><span class=\"pre\">configure_import_paths</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span></dt><dd><p>Configure import paths for game_router module.</p></dd>", "a[href=\"#dataflow.api.integrate_games.add_game_routes\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.integrate_games.add_game_routes\">\n<span class=\"sig-name descname\"><span class=\"pre\">add_game_routes</span></span><span class=\"sig-paren\">(</span><em class=\"sig-param\"><span class=\"n\"><span class=\"pre\">app</span></span><span class=\"p\"><span class=\"pre\">:</span></span><span class=\"w\"> </span><span class=\"n\"><a class=\"reference external\" href=\"https://fastapi.tiangolo.com/reference/fastapi/#fastapi.FastAPI\" title=\"(in FastAPI v0.0.0)\"><span class=\"pre\">fastapi.FastAPI</span></a></span></em>, <em class=\"sig-param\"><span class=\"n\"><span class=\"pre\">prefix</span></span><span class=\"p\"><span class=\"pre\">:</span></span><span class=\"w\"> </span><span class=\"n\"><a class=\"reference external\" href=\"https://docs.python.org/3/library/stdtypes.html#str\" title=\"(in Python v3.13)\"><span class=\"pre\">str</span></a></span><span class=\"w\"> </span><span class=\"o\"><span class=\"pre\">=</span></span><span class=\"w\"> </span><span class=\"default_value\"><span class=\"pre\">'/games'</span></span></em><span class=\"sig-paren\">)</span></dt><dd><p>Add game routes to the main API.</p><p>This function discovers game agents and adds routes for each game type\nto the provided FastAPI application. It creates both REST endpoints and\nWebSocket endpoints for real-time game state streaming.</p></dd>", "a[href=\"#attributes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-contents\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Module Contents<a class=\"headerlink\" href=\"#module-contents\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
