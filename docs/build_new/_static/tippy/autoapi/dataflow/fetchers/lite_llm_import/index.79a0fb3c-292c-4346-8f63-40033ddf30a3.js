selector_to_html = {"a[href=\"#dataflow.fetchers.lite_llm_import.logger\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.fetchers.lite_llm_import.logger\">\n<span class=\"sig-name descname\"><span class=\"pre\">logger</span></span></dt><dd></dd>", "a[href=\"#module-contents\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Module Contents<a class=\"headerlink\" href=\"#module-contents\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#functions\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Functions<a class=\"headerlink\" href=\"#functions\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#dataflow.fetchers.lite_llm_import.REQUESTS_AVAILABLE\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.fetchers.lite_llm_import.REQUESTS_AVAILABLE\">\n<span class=\"sig-name descname\"><span class=\"pre\">REQUESTS_AVAILABLE</span></span><em class=\"property\"><span class=\"w\"> </span><span class=\"p\"><span class=\"pre\">=</span></span><span class=\"w\"> </span><span class=\"pre\">True</span></em></dt><dd></dd>", "a[href=\"#dataflow.fetchers.lite_llm_import.LITELLM_URL\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.fetchers.lite_llm_import.LITELLM_URL\">\n<span class=\"sig-name descname\"><span class=\"pre\">LITELLM_URL</span></span><em class=\"property\"><span class=\"w\"> </span><span class=\"p\"><span class=\"pre\">=</span></span><span class=\"w\"> </span><span class=\"pre\">'https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json'</span></em></dt><dd></dd>", "a[href=\"#dataflow.fetchers.lite_llm_import.import_llm_models\"]": "<dt class=\"sig sig-object py\" id=\"dataflow.fetchers.lite_llm_import.import_llm_models\">\n<span class=\"sig-name descname\"><span class=\"pre\">import_llm_models</span></span><span class=\"sig-paren\">(</span><span class=\"sig-paren\">)</span> <span class=\"sig-return\"><span class=\"sig-return-icon\">\u2192</span> <span class=\"sig-return-typehint\"><a class=\"reference external\" href=\"https://docs.python.org/3/library/functions.html#bool\" title=\"(in Python v3.13)\"><span class=\"pre\">bool</span></a></span></span></dt><dd><p>Import LLM models from LiteLLM.</p></dd>", "a[href=\"#attributes\"]": "<h2 class=\"tippy-header\" style=\"margin-top: 0;\">Attributes<a class=\"headerlink\" href=\"#attributes\" title=\"Link to this heading\">\u00b6</a></h2>", "a[href=\"#module-dataflow.fetchers.lite_llm_import\"]": "<h1 class=\"tippy-header\" style=\"margin-top: 0;\">dataflow.fetchers.lite_llm_import<a class=\"headerlink\" href=\"#module-dataflow.fetchers.lite_llm_import\" title=\"Link to this heading\">\u00b6</a></h1><p>LiteLLM Importer for the Haive Registry System.</p><p>This module provides functionality for importing LLM models and\nproviders from LiteLLM\u2019s published model list.</p>"}
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
