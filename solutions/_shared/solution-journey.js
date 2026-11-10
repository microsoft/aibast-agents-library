(() => {
  'use strict';
  window.AibastJourney = {
    getLine(solution, pages) {
      return `Read ${new URL(`api/v1/solutions/${encodeURIComponent(solution.slug)}.json`, pages).href} and follow its setup instructions to get this agent running in my Copilot Studio. Use sample data only.`;
    },
    async copyText(text) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (error) {
        const field = document.createElement('textarea');
        field.value = text;
        document.body.appendChild(field);
        field.select();
        const copied = document.execCommand('copy');
        field.remove();
        return copied;
      }
    }
  };
})();
