# AIBAST Agents Library SDK

One script, no dependencies. It reads only the library's static API, so it works from any page.

```html
<script src="https://microsoft.github.io/aibast-agents-library/solutions/_shared/aibast-sdk.js"></script>
```

## Find and read solutions

```js
const list = await AibastLibrary.search();                 // one line per solution
const doc = await AibastLibrary.solution('tiered-huddle-board');
const scenario = await AibastLibrary.scenario(doc.try.scenarios[0].id);
const agent = await AibastLibrary.agent('tiered-huddle-board');
```

## Show a demo

```js
AibastDemo.mount('#demo', { scenario: 'tiered-huddle-board-board-view', surface: 'm365' });
```

Surfaces: `m365`, `cowork`, `studio`. Every answer is a recorded sample. Nothing connects to
anyone's data.

## Screenshots and narration

These files are not on the Pages site. They are served from raw.githubusercontent.com, pinned to
the commit the site was published from (`raw` in `api/registry.json`). The media map lists each
one with its sha256.

```js
const items = await AibastMedia.list('tiered-huddle-board');  // screenshots for one solution
const url = await AibastMedia.url(items[0].path);              // pinned raw URL
const blob = await AibastMedia.fetch(items[0].path);           // fetched and checked against sha256
```

## Without the script

Everything above is plain JSON. Start at `api/v1/index.json`, or read `llms.txt`.

`aibast-demo-sdk.js` is an alias, kept so existing pages keep working. It has `AibastDemo` only.

## Command line

```bash
python tools/aibast.py api build          # rebuild api/ and llms.txt
python tools/aibast.py api check          # fail if they do not match their sources
python tools/aibast.py media verify       # every screenshot and clip against its sha256
python tools/aibast.py media verify --live
python tools/aibast.py pages size         # build the Pages artifact and print its size
python tools/aibast.py demo check <slug> [--base <site address>]
```
