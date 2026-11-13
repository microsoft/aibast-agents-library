(() => {
  'use strict';
  window.AibastJourney = {
    solutionList(search, agents = [], demos = {agents: {}, scenarios: {}}) {
      const bySlug = new Map(agents.map(agent => [agent._solution?.package?.slug, agent]));
      return search.solutions.map(solution => {
        const agent = bySlug.get(solution.slug);
        const recorded = (demos.agents[agent?.name]?.scenarios || [])
          .filter(id => demos.scenarios[id]?.recorded).length;
        return {...solution, agent, recorded};
      });
    },
    scenarioId(id, solutions) {
      const slug = solutions.map(solution => solution.slug)
        .sort((a, b) => b.length - a.length)
        .find(slug => id === `${slug}-${slug}` || id.startsWith(`${slug}-${slug}-`));
      return slug ? id.slice(slug.length + 1) : id;
    },
    // The Cowork plugin is a release file of whichever copy of the library is being served.
    coworkPluginUrl(slug, hostname) {
      const owner = hostname.endsWith('.github.io') ? hostname.split('.')[0] : 'microsoft';
      return `https://github.com/${owner}/aibast-agents-library/releases/download/solution-bundles/${slug}-cowork-plugin.zip`;
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
