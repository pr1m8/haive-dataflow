selector_to_html = {"a[href=\"#dataflow.api.run_chess_api.main\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_chess_api.main\">\n<span class=\"sig-name descname\"><span class=\"pre\">main</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span></dt><dd><p>Parse arguments and run the chess API server.</p></dd>", "a[href=\"#module-contents\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Module Contents<a class=\"headerlink\" href=\"#module-contents\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#functions\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Functions<a class=\"headerlink\" href=\"#functions\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#attributes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#dataflow.api.run_chess_api.run_chess_api\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_chess_api.run_chess_api\">\n<span class=\"sig-name descname\"><span class=\"pre\">run_chess_api</span></span><span class=\"sig-paren\">(</span><em class=\"sig-param\"><span class=\"n\"><span class=\"pre\">port</span></span><span class=\"p\"><span class=\"pre\">:</span></span><span class=\"w\"> </span><span class=\"n\"><a class=\"reference external\" href=\"https://docs.python.org/3/library/functions.html#int\" title=\"(in Python v3.13)\"><span class=\"pre\">int</span></a></span><span class=\"w\"> </span><span class=\"o\"><span class=\"pre\">=</span></span><span class=\"w\"> </span><span class=\"default_value\"><span class=\"pre\">8000</span></span></em><span class=\"sig-paren\">)</span></dt><dd><p>Run the chess API server.</p></dd>", "a[href=\"#dataflow.api.run_chess_api.logger\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_chess_api.logger\">\n<span class=\"sig-name descname\"><span class=\"pre\">logger</span></span></dt><dd></dd>", "a[href=\"#module-dataflow.api.run_chess_api\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.run_chess_api<a class=\"headerlink\" href=\"#module-dataflow.api.run_chess_api\" title=\"Link to this heading\">\u00b6</a></h1><p>Chess API demonstration script.</p><p>This script launches a standalone API server for the chess game\nwith WebSocket support and Supabase integration.</p>", "a[href=\"#dataflow.api.run_chess_api.verify_environment\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_chess_api.verify_environment\">\n<span class=\"sig-name descname\"><span class=\"pre\">verify_environment</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span> <span class=\"sig-return\"><span class=\"sig-return-icon\">\u2192</span> <span class=\"sig-return-typehint\"><a class=\"reference external\" href=\"https://docs.python.org/3/library/functions.html#bool\" title=\"(in Python v3.13)\"><span class=\"pre\">bool</span></a></span></span></dt><dd><p>Verify that required environment variables are set.</p></dd>"}
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
