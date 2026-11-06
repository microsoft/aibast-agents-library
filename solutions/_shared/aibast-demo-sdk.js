/* AIBAST Agents Library demo SDK. One file, no dependencies, reads only the static library API.
 *
 *   <script src="https://microsoft.github.io/aibast-agents-library/solutions/_shared/aibast-demo-sdk.js"></script>
 *   AibastDemo.mount(element, {scenario: 'tiered-huddle-board-board-view', surface: 'm365'})  -> the iframe
 *   await AibastDemo.scenario('tiered-huddle-board-board-view')   -> api/v1/scenarios/<id>.json
 *   await AibastDemo.answer('tiered-huddle-board-board-view')     -> the recorded answer (rapp-preview-answer/1)
 *
 * Every answer is a recorded sample. Nothing here connects to anyone's data.
 */
(function (root) {
  'use strict';
  var script = document.currentScript;
  var base = (script && script.src) ? new URL('../../', script.src).href : new URL('./', location.href).href;
  var cache = {};

  function getJSON(path) {
    if (!cache[path]) {
      cache[path] = fetch(base + path).then(function (r) {
        if (!r.ok) throw new Error(path + ' returned ' + r.status);
        return r.json();
      });
    }
    return cache[path];
  }

  var AibastDemo = {
    base: base,
    mount: function (element, opts) {
      opts = opts || {};
      if (typeof element === 'string') element = document.querySelector(element);
      if (!element) throw new Error('AibastDemo.mount needs an element');
      if (!opts.scenario) throw new Error('AibastDemo.mount needs a scenario id');
      var q = new URLSearchParams({scenario: opts.scenario});
      if (opts.surface) q.set('surface', opts.surface);
      if (opts.autoplay) q.set('autoplay', '1');
      var frame = document.createElement('iframe');
      frame.src = base + 'solutions/_shared/m365-copilot-demo.html?' + q.toString();
      frame.title = opts.title || 'Agent preview with sample answers';
      frame.style.cssText = 'border:0;width:100%;height:' + (opts.height || '640px') + ';';
      frame.setAttribute('allow', 'clipboard-write');
      element.appendChild(frame);
      return frame;
    },
    scenario: function (id) { return getJSON('api/v1/scenarios/' + encodeURIComponent(id) + '.json'); },
    answer: function (id) { return AibastDemo.scenario(id).then(function (d) { return d.answer; }); },
    solution: function (slug) { return getJSON('api/v1/solutions/' + encodeURIComponent(slug) + '.json'); },
    search: function () { return getJSON('api/v1/search.json'); },
  };
  root.AibastDemo = AibastDemo;
})(window);
