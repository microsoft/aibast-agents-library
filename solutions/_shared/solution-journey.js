(() => {
  'use strict';
  window.AibastJourney = {
    solutionList(search, agents = []) {
      const bySlug = new Map(agents.map(agent => [agent._solution?.package?.slug, agent]));
      return search.solutions.map(solution => ({...solution, agent: bySlug.get(solution.slug)}));
    },
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
