# Client Health Score solution package

| Surface | Location |
| --- | --- |
| Portable agent | `agents/@aibast-agents-library/professional_services_stacks/client_health_score_stack/client_health_score_agent.py` |
| Deployment recipe | `solutions/client-health-score/deployment.json` |
| Live behavior gate | `tests/demo_cases/client-health-score.json` |
| PowerPoint evidence map | `solutions/client-health-score/evals/onepager-map.json` |
| Strict-isolation transcripts | `solutions/client-health-score/evals/transcripts.json` |
| Manual knowledge | `solutions/client-health-score/manual/knowledge/` |
| Manual skills | `solutions/client-health-score/manual/skills/` |

## Implemented scope

The package covers portfolio segmentation, synthetic churn indicators,
engagement analysis, satisfaction trends, at-risk prioritization, and
account-specific retention playbooks with stakeholder maps. Every client,
score, value, stakeholder, and action is fictional.

The indicators are decision support rather than validated predictions. The
agent never creates meetings, sends messages, makes concessions, changes
renewals, or writes to CRM.

The canonical transcript artifact was captured with only
`ClientHealthScoreAgent` discoverable and records all five persona cases as
passing.

<!-- scaffold-solution-journey:start -->
## Customer journey package map

| Surface | Location |
| --- | --- |
| Customer field guide | `solutions/client-health-score/field-guide.html` |
| Evidence report | `solutions/client-health-score/evidence-report.html` |
| Brainstem Easy Mode skill | `skills/aibast-easy-mode-brainstem/SKILL.md` |
| Copilot-only Easy Mode skill | `skills/aibast-easy-mode-copilot/SKILL.md` |
| Personless Easy-mode guide | `solutions/client-health-score/EASY-MODE-PERSONLESS.md` |
| Copilot-only Easy-mode comparison | `solutions/client-health-score/EASY-MODE-COPILOT-CHAT.md` |
| Guided Easy/Hard quest | `solutions/client-health-score/quest.html` |
| Literal browser tutorial | `solutions/client-health-score/manual-tutorial.html` |
| Raw export manifest | `solutions/client-health-score/export-manifest.json` |
| Source bundle | `solutions/client-health-score/exports/client-health-score-source.zip` |
| Manual evidence | `solutions/client-health-score/evals/manual-build-evidence.json` |
| Manual browserfilm | `solutions/client-health-score/screenshots/manual/browserfilm.json` |

**Scaffold status:** 73 resources ready; 0 pending. Manual evidence and referenced screenshots passed scaffold validation.

The journey uses synthetic inputs and qualitative proof. It is not a customer
KPI, live-system result, production-readiness claim, or publication approval.
<!-- scaffold-solution-journey:end -->
