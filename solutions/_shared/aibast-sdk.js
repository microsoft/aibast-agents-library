/* AIBAST Agents Library SDK. One file, no dependencies, reads only the static library API.
 *
 *   <script src="https://microsoft.github.io/aibast-agents-library/solutions/_shared/aibast-sdk.js"></script>
 *
 *   await AibastLibrary.search()                     -> api/v1/search.json (one line per solution)
 *   await AibastLibrary.solution('tiered-huddle-board')
 *   await AibastLibrary.scenario('tiered-huddle-board-board-view')
 *   await AibastLibrary.agent('tiered-huddle-board')  -> api/v1/catalog/<name>.json
 *
 *   await AibastMedia.url('solutions/<slug>/screenshots/...png')   -> pinned raw URL
 *   await AibastMedia.fetch(path)                     -> a Blob, checked against its sha256
 *   await AibastMedia.list('tiered-huddle-board')     -> api/v1/media/<group>.json items
 *
 *   AibastDemo.mount(element, {scenario: 'tiered-huddle-board-board-view', surface: 'm365'})
 *
 * Screenshots and narration are served from raw.githubusercontent.com, pinned to the commit the
 * site was published from (registry.json "raw"); everything else comes from this site.
 * Every answer is a recorded sample. Nothing here connects to anyone's data.
 * aibast-demo-sdk.js is an alias kept for existing pages; it exposes the same AibastDemo.
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
  function id(value) { return encodeURIComponent(value); }
  function hex(buffer) {
    return Array.prototype.map.call(new Uint8Array(buffer), function (b) { return ('0' + b.toString(16)).slice(-2); }).join('');
  }

  var AibastLibrary = {
    base: base,
    registry: function () { return getJSON('api/registry.json'); },
    index: function () { return getJSON('api/v1/index.json'); },
    search: function () { return getJSON('api/v1/search.json'); },
    solution: function (slug) { return getJSON('api/v1/solutions/' + id(slug) + '.json'); },
    scenario: function (sid) { return getJSON('api/v1/scenarios/' + id(sid) + '.json'); },
    agent: function (name) { return getJSON('api/v1/catalog/' + id(name) + '.json'); },
    stacks: function () { return getJSON('api/v1/stacks.json'); },
  };

  var groups = null;
  function mediaIndex() {
    if (!groups) {
      groups = getJSON('api/v1/media/index.json').then(function (index) {
        return Promise.all(index.groups.map(function (g) { return getJSON(g.doc); })).then(function (docs) {
          var byPath = {};
          docs.forEach(function (doc) { doc.items.forEach(function (item) { byPath[item.path] = item; }); });
          return byPath;
        });
      });
    }
    return groups;
  }

  var AibastMedia = {
    index: function () { return getJSON('api/v1/media/index.json'); },
    list: function (group) { return getJSON('api/v1/media/' + id(group) + '.json').then(function (d) { return d.items; }); },
    item: function (path) { return mediaIndex().then(function (byPath) { return byPath[path] || null; }); },
    url: function (path) {
      return AibastLibrary.registry().then(function (r) { return r.raw + path.split('/').map(id).join('/'); });
    },
    fetch: function (path) {
      return Promise.all([AibastMedia.item(path), AibastMedia.url(path)]).then(function (both) {
        var item = both[0], url = both[1];
        if (!item) throw new Error(path + ' is not in the media map');
        return fetch(url).then(function (r) {
          if (!r.ok) throw new Error(path + ' returned ' + r.status);
          return r.arrayBuffer();
        }).then(function (buffer) {
          if (!(root.crypto && root.crypto.subtle)) throw new Error('AibastMedia.fetch checks sha256 and needs a secure (https) page; use AibastMedia.url on plain http');
          return crypto.subtle.digest('SHA-256', buffer).then(function (digest) {
            if (hex(digest) !== item.sha256) throw new Error(path + ' failed its sha256 check');
            return new Blob([buffer], {type: item.mimeType});
          });
        });
      });
    },
  };

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
    scenario: AibastLibrary.scenario,
    answer: function (sid) { return AibastLibrary.scenario(sid).then(function (d) { return d.answer; }); },
    solution: AibastLibrary.solution,
    search: AibastLibrary.search,
  };

  root.AibastLibrary = AibastLibrary;
  root.AibastMedia = AibastMedia;
  root.AibastDemo = AibastDemo;
})(window);
