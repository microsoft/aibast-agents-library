(() => {
  'use strict';
  window.AibastJourney = {
    getLine(solution, pages) {
      return solution.get.prompt.replace('{pages}', pages);
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
