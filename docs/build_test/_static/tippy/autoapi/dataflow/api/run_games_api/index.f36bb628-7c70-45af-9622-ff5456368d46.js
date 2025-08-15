selector_to_html = {"a[href=\"#dataflow.api.run_games_api.haive_root\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_games_api.haive_root\">\n<span class=\"sig-name descname\"><span class=\"pre\">haive_root</span></span><em class=\"property\"><span class=\"w\"> </span><span class=\"p\"><span class=\"pre\">=</span></span><span class=\"w\"> </span><span class=\"pre\">b'.'</span></em></dt><dd></dd>", "a[href=\"#dataflow.api.run_games_api.haive_games_path\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_games_api.haive_games_path\">\n<span class=\"sig-name descname\"><span class=\"pre\">haive_games_path</span></span></dt><dd></dd>", "a[href=\"#dataflow.api.run_games_api.packages_dir\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_games_api.packages_dir\">\n<span class=\"sig-name descname\"><span class=\"pre\">packages_dir</span></span></dt><dd></dd>", "a[href=\"#module-dataflow.api.run_games_api\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.api.run_games_api<a class=\"headerlink\" href=\"#module-dataflow.api.run_games_api\" title=\"Link to this heading\">\u00b6</a></h1><p>Run the Haive Games API with dynamic game discovery.</p><p>This script runs a standalone API for game agents with dynamic discovery\nfrom the haive-games package. It creates WebSocket endpoints for each\ndiscovered game agent and provides HTML clients for testing.</p>", "a[href=\"#dataflow.api.run_games_api.create_app\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_games_api.create_app\">\n<span class=\"sig-name descname\"><span class=\"pre\">create_app</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span></dt><dd><p>Create FastAPI app with game routes.</p></dd>", "a[href=\"#functions\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Functions<a class=\"headerlink\" href=\"#functions\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#dataflow.api.run_games_api.src_dir\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_games_api.src_dir\">\n<span class=\"sig-name descname\"><span class=\"pre\">src_dir</span></span><em class=\"property\"><span class=\"w\"> </span><span class=\"p\"><span class=\"pre\">=</span></span><span class=\"w\"> </span><span class=\"pre\">b'.'</span></em></dt><dd></dd>", "a[href=\"#dataflow.api.run_games_api.logger\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_games_api.logger\">\n<span class=\"sig-name descname\"><span class=\"pre\">logger</span></span></dt><dd></dd>", "a[href=\"#dataflow.api.run_games_api.current_dir\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_games_api.current_dir\">\n<span class=\"sig-name descname\"><span class=\"pre\">current_dir</span></span></dt><dd></dd>", "a[href=\"#dataflow.api.run_games_api.main\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.api.run_games_api.main\">\n<span class=\"sig-name descname\"><span class=\"pre\">main</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span></dt><dd><p>Run the games API server.</p></dd>", "a[href=\"#attributes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-contents\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Module Contents<a class=\"headerlink\" href=\"#module-contents\" title=\"Link to this heading\">\u00b6</a></h2>"}
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
